from api.models.managers import BaseManager


class SubtaskUpdateCounterManager(BaseManager):
    def increment_count(self, project_id: int, /) -> None:
        counter = self.get_queryset().filter(project=project_id).first()
        if counter:
            counter.count += 1
            counter.save(update_fields=['count'])
        else:
            self.get_queryset().create(project_id=project_id)
