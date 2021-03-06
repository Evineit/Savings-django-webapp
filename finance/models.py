import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .util import next_payment_date, update_children, cycles_at_date


# Create your models here.
class User(AbstractUser):
    def del_accounts(self):
        for account in self.accounts.all():
            account.delete()


class Account(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="accounts")
    balance = models.DecimalField(decimal_places=3, max_digits=10)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name}:{self.balance}"

    def update_balance(self):
        for rec_expense in self.rec_expenses.all():
            rec_expense.update_children()
        incomes = sum([x.amount for x in Income.objects.filter(account=self)])
        expenses = sum([x.amount for x in Expense.objects.filter(account=self)])
        self.balance = incomes - expenses
        self.save()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance
        }


class Income(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="incomes")
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    added_date = models.DateTimeField(default=timezone.now)
    recurring_parent = models.ForeignKey("RecurringIncome", on_delete=models.CASCADE, related_name="children",
                                         null=True, blank=True)

    def __str__(self):
        return f"id: {self.id},account:{self.account.name},amount: {self.amount}, date:{self.added_date}"

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "added_date": self.added_date.strftime("%b %d %Y, %I:%M %p"),
            "timestamp": self.added_date.timestamp(),
            "parent_id": self.recurring_parent.id if self.recurring_parent else None,
            "parent_title": self.recurring_parent.description if self.recurring_parent else None,
        }


class Expense(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    added_date = models.DateTimeField(default=timezone.now)
    recurring_parent = models.ForeignKey("RecurringPayment", on_delete=models.CASCADE, related_name="children",
                                         null=True, blank=True)

    def __str__(self):
        return f"id: {self.id},amount: {self.amount}, date:{self.added_date}"

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "added_date": self.added_date.strftime(r"%b %d %Y, %I:%M %p"),
            "timestamp": self.added_date.timestamp(),
            "parent_id": self.recurring_parent.id if self.recurring_parent else None,
            "parent_title": self.recurring_parent.description if self.recurring_parent else None,
        }


class RecurringPayment(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="rec_expenses")
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    schedule_type = models.CharField(max_length=50)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "start_date": self.start_date.strftime(r"%b %d %Y, %I:%M %p"),
            "next_date": self.next_payment_date().strftime(r"%d %b %Y"),
            "next_date_timestamp": self.next_payment_date().timestamp(),
            "schedule_type": self.schedule_type,
        }

    def cycles_at_date(self, date: datetime = timezone.now()) -> int:
        return cycles_at_date(self, date)

    def update_children(self, date=timezone.now()):
        update_children(self, Expense, date)

    def next_payment_date(self, date=timezone.now()):
        return next_payment_date(self, date)


class RecurringIncome(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="rec_incomes")
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    schedule_type = models.CharField(max_length=50)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "start_date": self.start_date.strftime(r"%b %d %Y, %I:%M %p"),
            "next_date": self.next_payment_date().strftime(r"%d %b %Y"),
            "next_date_timestamp": self.next_payment_date().timestamp(),
            "schedule_type": self.schedule_type,
        }

    def cycles_at_date(self, date: datetime = timezone.now()) -> int:
        return cycles_at_date(self, date)

    def update_children(self, date=timezone.now()):
        update_children(self, Income, date)

    def next_payment_date(self, date=timezone.now()):
        return next_payment_date(self, date)
