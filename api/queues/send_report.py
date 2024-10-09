from api.queues.core.base import use_rq_if_configured
from typing import Optional

from api.queues.rq.send_report import send_client_csv_report as send_client_csv_report_rq, \
    send_client_pdf_report as send_client_pdf_report_rq, \
    send_csv_report as send_csv_report_rq, \
    send_pdf_report as send_pdf_report_rq, \
    send_handover_information_csv_report_rq as send_handover_information_csv_report_rq

from api.queues.celery.send_report import send_client_csv_report as send_client_csv_report_celery, \
    send_client_pdf_report as send_client_pdf_report_celery, \
    send_csv_report as send_csv_report_celery, \
    send_pdf_report as send_pdf_report_celery, \
    send_handover_information_csv_report as send_handover_information_csv_report_celery


@use_rq_if_configured(send_client_csv_report_rq)
def send_client_csv_report(request, model, project: int, to_email: str):
    send_client_csv_report_celery.delay(request=request, model=model, project=project, to_email=to_email)


@use_rq_if_configured(send_client_pdf_report_rq)
def send_client_pdf_report(request, model, project: int, to_email: str):
    send_client_pdf_report_celery.delay(request=request, model=model, project=project, to_email=to_email)


@use_rq_if_configured(send_handover_information_csv_report_rq)
def send_handover_information_csv_report(request, model, project: int, to_email: str):
    send_handover_information_csv_report_celery.delay(request=request, model=model,
                                                      project=project, to_email=to_email)


@use_rq_if_configured(send_csv_report_rq)
def send_csv_report(request, model, project: Optional[int], to_email: str):
    send_csv_report_celery.delay(request=request, model=model, project=project, to_email=to_email)


@use_rq_if_configured(send_pdf_report_rq)
def send_pdf_report(request, model, project: int, to_email: str):
    send_pdf_report_celery.delay(request=request, model=model, project=project, to_email=to_email)
