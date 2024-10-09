from typing import Optional

from api.services.entity_report_service import EntityReportService


def send_client_csv_report(request, model, project: int, to_email: str):
    EntityReportService(request=request, model=model, project=project, to_email=to_email).send_client_csv_report()


def send_client_pdf_report(request, model, project: int, to_email: str):
    EntityReportService(request=request, model=model, project=project, to_email=to_email).send_client_pdf_report()


def send_handover_information_csv_report(request, model, project: int, to_email: str):
    EntityReportService(request=request, model=model,
                        project=project, to_email=to_email).send_handover_information_csv_report()


def send_csv_report(request, model, project: Optional[int], to_email: str):
    EntityReportService(request=request, model=model, project=project, to_email=to_email).send_csv_report()


def send_pdf_report(request, model, project: int, to_email: str):
    EntityReportService(request=request, model=model, project=project, to_email=to_email).send_pdf_report()
