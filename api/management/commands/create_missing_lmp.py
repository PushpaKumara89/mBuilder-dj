from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count, Prefetch

from api.models import PackageMatrix, Project, LocationMatrix, LocationMatrixPackage


class Command(BaseCommand):
    help = "Create missing tasks for checked location matrix packages."

    def add_arguments(self, parser):
        parser.add_argument('project_pk', type=int)

    def handle(self, *args, **options):
        project = options['project_pk']

        try:
            project = Project.objects.get(pk=project)
        except Project.DoesNotExist:
            raise CommandError('Project "%s" does not exist.' % project)

        self.stdout.write(self.style.WARNING('Start creating lmp for project %s' % project.pk))

        package_matrices = PackageMatrix.objects.select_related('package', 'package_activity').filter(project=project).all()
        package_activities = list(map(lambda pm: pm.package_activity, package_matrices))

        count_lmp_with_deleted_pa = LocationMatrixPackage.objects.filter(package_activity__deleted__isnull=False, package_matrix__project_id=project.pk).count()
        if count_lmp_with_deleted_pa > 0:
            LocationMatrixPackage.objects.filter(package_activity__deleted__isnull=False,
                                                 package_matrix__project_id=project.pk).delete()

            self.stdout.write(self.style.WARNING('Deleted location matrix packages with deleted package activity %s' % count_lmp_with_deleted_pa))

        location_matrices = LocationMatrix.objects.prefetch_related(
            Prefetch('locationmatrixpackage_set', queryset=LocationMatrixPackage.objects.filter(deleted__isnull=True).all())
        ).annotate(
            lmp_count=Count('locationmatrixpackage', filter=Q(locationmatrixpackage__deleted__isnull=True))).filter(
            project_id=project.id, lmp_count__lt=len(package_activities)
        ).all()

        location_matrix_packages = []
        restored_lmp_count = 0

        for location_matrix in location_matrices:
            self.stdout.write(self.style.WARNING('Start creating lmp for location matrix %s.' % location_matrix.pk))

            used_activities = set(location_matrix.locationmatrixpackage_set.values_list('package_activity_id', flat=True))
            unused_activities = list(filter(lambda pa: pa not in used_activities, package_activities))

            for unused_activity in unused_activities:
                self.stdout.write(self.style.WARNING('Start creating lmp for location matrix %s, package activity %s.' % (location_matrix.pk, unused_activity.pk)))

                pm = package_matrices.filter(package_activity_id=unused_activity.pk).get()

                lmp = LocationMatrixPackage.all_objects.filter(package_matrix_id=pm.id, location_matrix_id=location_matrix.pk).first()
                if lmp and lmp.deleted:
                    lmp.undelete()
                    restored_lmp_count += 1
                elif lmp:
                    continue
                else:
                    location_matrix_packages.append(
                        LocationMatrixPackage(
                            package_id=pm.package_id,
                            package_activity_id=unused_activity.pk,
                            location_matrix_id=location_matrix.pk,
                            enabled=False,
                            package_activity_name=unused_activity.name,
                            package_matrix_id=pm.id
                        ))

                self.stdout.write(self.style.WARNING('Creating lmp for location matrix %s, package activity %s has been finished.' % (location_matrix.pk, unused_activity.pk)))

            self.stdout.write(self.style.WARNING('Creating lmp for location matrix %s has been finished.' % location_matrix.pk))

        self.stdout.write(self.style.WARNING('Created %s lmp.' % len(location_matrix_packages)))
        self.stdout.write(self.style.WARNING('Restored %s lmp.' % restored_lmp_count))

        LocationMatrixPackage.objects.bulk_create(location_matrix_packages)

        self.stdout.write(self.style.WARNING('Creating lmp for project %s has been finished.' % project.pk))
