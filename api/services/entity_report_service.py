from typing import Type, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import TextChoices
from pydash import human_case
from rest_framework.request import Request

from api.mails.report.client_report_created import ClientReportCreated
from api.mails.report.created import ReportCreated
from api.mails.report.handover_information_created import HandoverInformationReportCreated
from api.models import Task, Subtask, PackageHandoverDocumentMedia, AssetHandoverDocumentMedia, Media, QualityIssue, \
    Project, HandoverDocument, Package, PackageMatrix, LocationMatrix, LocationMatrixPackage, Company, PackageActivity
from api.models.base_model import BaseModel
from api.services.media_entity_service import MediaEntityService
from api.utilities.report_generators import TaskReportGenerator, SubtaskReportGenerator, QualityIssueReportGenerator, \
    PackageHandoverDocumentMediaReportGenerator, AssetHandoverDocumentMediaReportGenerator, BaseReportGenerator
from api.utilities.report_generators.asset_handover_information_report_generator import \
    AssetHandoverInformationReportGenerator
from api.utilities.report_generators.company_report_generator import CompanyReportGenerator
from api.utilities.report_generators.handover_document_report_generator import HandoverDocumentReportGenerator
from api.utilities.report_generators.location_matrix_package_report_generator import LocationMatrixPackageReportGenerator
from api.utilities.report_generators.package_handover_information_report_generator import \
    PackageHandoverInformationReportGenerator
from api.utilities.report_generators.package_matrix_report_generator import PackageMatrixGenerator
from api.utilities.report_generators.location_matrix_report_generator import LocationMatrixReportGenerator
from api.utilities.report_generators.package_activity_report_generator import PackageActivityReportGenerator
from api.utilities.report_generators.package_report_generator import PackageReportGenerator
from api.utilities.report_generators.project_report_generator import ProjectReportGenerator
from api.utilities.report_generators.task_client_report_generator import TaskClientReportGenerator
from api.utilities.report_generators.user_report_generator import UserReportGenerator

User = get_user_model()


class EntityReportService:
    class ReportType(TextChoices):
        CSV = 'csv'
        PDF = 'pdf'

    model_class: Type[BaseModel]
    project: Project = None
    to_email: str
    request: Request
    entity_name_in_human_case: str

    def __init__(self, request: Request, model: BaseModel, project: Optional[int], to_email: str):
        self.request = request
        self.model_class = model
        if project is not None:
            self.project = Project.objects.filter(id=project).get()
        self.to_email = to_email
        self.entity_name_in_human_case = human_case(self.model_class.__name__).title()

    def send_csv_report(self) -> None:
        generated_file = self.__get_report_generator().generateCsv()
        report = self.__save_report(generated_file)
        subject = self.__get_entity_report_email_subject(self.ReportType.CSV)
        self.__send_email(report, self.ReportType.CSV, subject, ReportCreated)

    def send_client_csv_report(self) -> None:
        generated_file = self.__get_client_report_generator().generateCsv()
        report = self.__save_report(generated_file)
        subject = self.__get_client_entity_report_email_subject(self.ReportType.CSV)
        self.__send_email(report, self.ReportType.CSV, subject, ClientReportCreated)

    def send_client_pdf_report(self) -> None:
        generated_file = self.__get_client_report_generator().generatePdf()
        report = self.__save_report(generated_file)
        subject = self.__get_client_entity_report_email_subject(self.ReportType.PDF)
        self.__send_email(report, self.ReportType.PDF, subject, ClientReportCreated)

    def send_handover_information_csv_report(self) -> None:
        generated_file = self.__get_handover_information_report_generator().generateCsv()
        report = self.__save_report(generated_file)
        subject = self.__get_handover_information_report_email_subject()
        self.__send_email(report, self.ReportType.CSV, subject, HandoverInformationReportCreated)

    def send_pdf_report(self) -> None:
        generated_file = self.__get_report_generator().generatePdf()
        report = self.__save_report(generated_file)
        subject = self.__get_entity_report_email_subject(self.ReportType.PDF)
        self.__send_email(report, self.ReportType.PDF, subject, ReportCreated)

    def __get_report_generator(self) -> BaseReportGenerator:
        generator_class = self.__get_report_generator_class()
        return generator_class(project=self.project, model=self.model_class, request=self.request)

    def __get_client_report_generator(self) -> BaseReportGenerator:
        generator_class = self.__get_client_report_generator_class()
        return generator_class(project=self.project, model=self.model_class, request=self.request)

    def __get_handover_information_report_generator(self) -> BaseReportGenerator:
        generator_class = self.__get_handover_information_report_generator_class()
        return generator_class(project=self.project, model=self.model_class, request=self.request)

    def __get_report_generator_class(self) -> Type[BaseReportGenerator]:
        if self.model_class == Task:
            return TaskReportGenerator
        elif self.model_class == Subtask:
            return SubtaskReportGenerator
        elif self.model_class == QualityIssue:
            return QualityIssueReportGenerator
        elif self.model_class == Company:
            return CompanyReportGenerator
        elif self.model_class == PackageHandoverDocumentMedia:
            return PackageHandoverDocumentMediaReportGenerator
        elif self.model_class == AssetHandoverDocumentMedia:
            return AssetHandoverDocumentMediaReportGenerator
        elif self.model_class == HandoverDocument:
            return HandoverDocumentReportGenerator
        elif self.model_class == LocationMatrix:
            return LocationMatrixReportGenerator
        elif self.model_class == User:
            return UserReportGenerator
        elif self.model_class == Project:
            return ProjectReportGenerator
        elif self.model_class == Package:
            return PackageReportGenerator
        elif self.model_class == LocationMatrixPackage:
            return LocationMatrixPackageReportGenerator
        elif self.model_class == PackageMatrix:
            return PackageMatrixGenerator
        elif self.model_class == PackageActivity:
            return PackageActivityReportGenerator

        raise ValueError('Invalid report model')

    def __get_client_report_generator_class(self) -> Type[BaseReportGenerator]:
        if self.model_class == Task:
            return TaskClientReportGenerator

        raise ValueError('Invalid report model')

    def __get_handover_information_report_generator_class(self) -> Type[BaseReportGenerator]:
        if self.model_class == PackageHandoverDocumentMedia:
            return PackageHandoverInformationReportGenerator
        elif self.model_class == AssetHandoverDocumentMedia:
            return AssetHandoverInformationReportGenerator

        raise ValueError('Invalid report model')

    def __save_report(self, generated_file: SimpleUploadedFile) -> Media:
        return MediaEntityService().save_report({'file': generated_file, 'is_public': False})

    def __send_email(self, report: Media, report_type: ReportType, subject: str, email_class) -> None:
        email_context = {
            'report_type': report_type,
            'project_name': self.project.name if self.project else '',
            'entity_name': self.entity_name_in_human_case,
            'support_email': settings.EMAIL_SUPPORT_EMAIL,
            'report': report
        }

        email_class(). \
            set_subject(subject). \
            set_to(self.to_email). \
            set_context(email_context). \
            send()

    def __get_entity_report_email_subject(self, report_type: ReportType) -> str:
        entity_name = self.__get_entity_name()
        return '%s %s report has been generated' % (entity_name, report_type.upper())

    def __get_client_entity_report_email_subject(self, report_type: ReportType) -> str:
        entity_name = self.__get_entity_name()
        return '%s %s report for Client has been generated' % (entity_name, report_type.upper())

    def __get_handover_information_report_email_subject(self) -> str:
        return 'Handover Information Report has been generated'

    def __get_entity_name(self) -> str:
        if self.model_class == Task:
            entity_name = 'Quality Report'
        elif self.model_class == Subtask:
            entity_name = 'Rework and Defects'
        elif self.model_class == PackageHandoverDocumentMedia:
            entity_name = 'Package Handover'
        elif self.model_class == AssetHandoverDocumentMedia:
            entity_name = 'Asset Handover'
        elif self.model_class == HandoverDocument:
            entity_name = 'Handover Information'
        else:
            entity_name = self.entity_name_in_human_case

        return entity_name