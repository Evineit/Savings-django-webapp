from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=50)

class Account(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="accounts")
    balance = models.DecimalField(decimal_places=3,max_digits=10)
    name = models.CharField(max_length= 50, blank=True)

class Income(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="incomes")


class Expense(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name="expenses")


class RecurringPayment(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    schedule_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="recpayments")
    

class RecurringIncome(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    schedule_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name="recincomes")