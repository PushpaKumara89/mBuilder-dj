from typing import Optional
from django_rq import job

from api.queues.core.send_report import send_client_csv_report as send_client_csv_report_core, \
    send_client_pdf_report as send_client_pdf_report_core, \
    send_csv_report as send_csv_report_core, \
    send_pdf_report as send_pdf_report_core, \
    send_handover_information_csv_report as send_package_handover_information_csv_report_core


@job('reports', timeout=36000)
def send_client_csv_report(request, model, project: int, to_email: str):
    send_client_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@job('reports', timeout=36000)
def send_client_pdf_report(request, model, project: int, to_email: str):
    send_client_pdf_report_core(request=request, model=model, project=project, to_email=to_email)


@job('reports', timeout=36000)
def send_handover_information_csv_report_rq(request, model, project: int, to_email: str):
    send_package_handover_information_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@job('reports', timeout=36000)
def send_csv_report(request, model, project: Optional[int], to_email: str):
    send_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@job('reports', timeout=36000)
def send_pdf_report(request, model, project: int, to_email: str):
    send_pdf_report_core(request=request, model=model, project=project, to_email=to_email)
