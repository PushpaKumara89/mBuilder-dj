from django.db import models
from safedelete import SOFT_DELETE

from api.models import Project
from api.models.base_model import BaseModel


class ProjectNews(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'project_news'

    title = models.CharField(max_length=255)
    text = models.TextField()
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
