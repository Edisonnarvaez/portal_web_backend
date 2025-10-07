from django.db import models

from .process_type import ProcessType
from .department import Department
from users.models import User

class Process(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    processType = models.ForeignKey(ProcessType, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    

    def __str__(self):
        return self.name