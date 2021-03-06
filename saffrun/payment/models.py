from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
from profile.models import UserProfile, EmployeeProfile
from core.models import BaseModel


class Invoice(BaseModel):
    debtor = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(EmployeeProfile, on_delete=models.DO_NOTHING, null=True)
    token = models.CharField(max_length=12)
    reference_code = models.CharField(max_length=24)
    amount = models.IntegerField()
    is_wallet_invoice = models.BooleanField(default=False)
    filters = models.JSONField()
