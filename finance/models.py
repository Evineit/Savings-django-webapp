import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .util import *

# Create your models here.
class User(AbstractUser):
    def del_accounts(self):
        for account in self.accounts.all():
            account.delete()

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"

class Account(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="accounts")
    balance = models.DecimalField(decimal_places=3,max_digits=10)
    name = models.CharField(max_length= 50, blank=True)
    def __str__(self):
        return f"{self.name}:{self.balance}"
    def update_balance(self):
        for rec_expense in self.rec_expenses.all():
            rec_expense.update_children()
        incomes = sum([x.amount for x in Income.objects.filter(account = self)])
        expenses = sum([x.amount for x in Expense.objects.filter(account = self)])
        self.balance = incomes - expenses
        self.save()

class Income(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="incomes")
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="incomes")
    recurring_parent = models.ForeignKey("RecurringIncome", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    def __str__(self):
        return f"id: {self.id},account:{self.account.name},amount: {self.amount}, date:{self.added_date}"


class Expense(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="expenses")
    recurring_parent = models.ForeignKey("RecurringPayment", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    def __str__(self):
        return f"id: {self.id},amount: {self.amount}, date:{self.added_date}"


class RecurringPayment(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="rec_expenses")
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    schedule_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="recpayments")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category.name,
            # "added_date": maybe,
            "start_date": self.start_date.strftime("%b %-d %Y, %-I:%M %p"),
            # "end_date": self.end_date.strftime("%b %-d %Y, %-I:%M %p"),
            "next_date": self.next_payment_date().strftime(r"%d %b %Y") ,
            "schedule_type": self.schedule_type,
        }

    def cycles_at_date(self, date:datetime = timezone.now()) -> int:
        return cycles_at_date(self,date)
    def update_children(self,date = timezone.now()):
        update_children(self,Expense,date)
    def next_payment_date(self, date= timezone.now()):
        return next_payment_date(self,date)
            
    

class RecurringIncome(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="rec_incomes")
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    schedule_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="recincomes")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category.name,
            # "added_date": maybe,
            "start_date": self.start_date.strftime("%b %-d %Y, %-I:%M %p"),
            # "end_date": self.end_date.strftime("%b %-d %Y, %-I:%M %p"),
            "next_date": self.next_payment_date().strftime(r"%d %b %Y") ,
            "schedule_type": self.schedule_type,
        }
    def cycles_at_date(self, date:datetime = timezone.now()) -> int:
        return cycles_at_date(self,date)
    def update_children(self, date = timezone.now()):
        update_children(self,Income,date)
    def next_payment_date(self, date= timezone.now()):
        return next_payment_date(self,date)

