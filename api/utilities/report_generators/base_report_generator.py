from abc import abstractmethod, ABC
from typing import Type

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.request import Request

from api.models import Project
from api.models.base_model import BaseModel


class BaseReportGenerator(ABC):
    def __init__(self, project: Project, model: Type[BaseModel], request: Request):
        self.model = model
        self.project = project
        self.request = request

    @abstractmethod
    def generatePdf(self) -> SimpleUploadedFile:
        ...

    @abstractmethod
    def generateCsv(self) -> SimpleUploadedFile:
        ...
