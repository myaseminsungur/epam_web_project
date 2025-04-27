from django.db import models

# Create your models here.

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)

class ExchangeRate(models.Model):
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_rates')
    target_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='target_rates')
    rate = models.DecimalField(max_digits=20, decimal_places=6)
    date = models.DateField()
