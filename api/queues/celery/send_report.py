from mbuild.settings import app as celery_app

from typing import Optional

from api.queues.core.send_report import send_client_csv_report as send_client_csv_report_core, \
    send_client_pdf_report as send_client_pdf_report_core, \
    send_csv_report as send_csv_report_core, \
    send_pdf_report as send_pdf_report_core, \
    send_handover_information_csv_report as send_handover_information_csv_report_core


@celery_app.task(queue='reports', time_limit=36000)
def send_client_csv_report(request, model, project: int, to_email: str):
    send_client_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@celery_app.task(queue='reports', time_limit=36000)
def send_client_pdf_report(request, model, project: int, to_email: str):
    send_client_pdf_report_core(request=request, model=model, project=project, to_email=to_email)


@celery_app.task(queue='reports', time_limit=36000)
def send_handover_information_csv_report(request, model, project: int, to_email: str):
    send_handover_information_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@celery_app.task(queue='reports', time_limit=36000)
def send_csv_report(request, model, project: Optional[int], to_email: str):
    send_csv_report_core(request=request, model=model, project=project, to_email=to_email)


@celery_app.task(queue='reports', time_limit=36000)
def send_pdf_report(request, model, project: int, to_email: str):
    send_pdf_report_core(request=request, model=model, project=project, to_email=to_email)
