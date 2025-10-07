from django.db import models
from users.models import User
from .company import Company

class ProcessType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    

    def __str__(self):
        return self.name