import datetime
from datetime import date, time
from django.contrib.auth.models import AbstractUser
from django.db import models
import calendar
from django.utils import timezone
from django.utils.timezone import make_aware

# Create your models here.
class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"

class Account(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="accounts")
    balance = models.DecimalField(decimal_places=3,max_digits=10)
    name = models.CharField(max_length= 50, blank=True)

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
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="incomes")
    recurring_parent = models.ForeignKey("RecurringIncome", on_delete=models.CASCADE, related_name="incomes", null=True, blank=True)
    def __str__(self):
        return f"account: {self.account.name},amount: {self.amount}, date{self.added_date}, category: {self.category.name}"


class Expense(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name="expenses")
    recurring_parent = models.ForeignKey("RecurringPayment", on_delete=models.CASCADE, related_name="expenses", null=True, blank=True)
    # def __str__(self):
    #     return f"account: {self.account.name},amount: {self.amount}, date{self.added_date}, category: {self.category.name}"
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
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="recpayments")

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
        if timezone.is_naive(date): date = make_aware(date)
        if self.schedule_type == "Custom":
            if self.end_date and date > self.end_date:
                delta = self.end_date - self.start_date
                return delta.days
            delta = date - self.start_date
            return delta.days
        elif self.schedule_type == "Monthly":
            counter = 0
            new_date = self.start_date
            while new_date < date:
                new_date = add_months(new_date,1)
                if self.end_date and new_date > self.end_date:
                    break
                if new_date > date:
                    break
                elif new_date <= date:
                    counter += 1
            return counter
        elif self.schedule_type == "Yearly":
            counter = 0
            new_date = self.start_date
            while new_date < date:
                new_date = add_months(new_date,12)
                if self.end_date and new_date > self.end_date:
                    break
                if new_date > date:
                    break
                elif new_date <= date:
                    counter += 1
            return counter
    
    # Adds the necessary expenses based on the current amount 
    def update_children(self,date = timezone.now()):
        cycles = self.cycles_at_date(date) 
        expenses = self.expenses.all().count()
        new_date = self.start_date
        
        while (expenses <= cycles ):
            if self.schedule_type == "Custom":
                new_date = self.start_date + datetime.timedelta(days=expenses)
            elif self.schedule_type == "Monthly":
                new_date = add_months(self.start_date,expenses)
            elif self.schedule_type == "Yearly":
                new_date = add_months(self.start_date,expenses*12)
            Expense.objects.create(
                    account= self.account,
                    amount = self.amount,
                    added_date = make_aware(datetime.datetime.combine(new_date, datetime.datetime.min.time())),
                    category = self.category,
                    recurring_parent = self
            ) 
            expenses = self.expenses.all().count()
    def next_payment_date(self, date= timezone.now()):
        cycles = self.cycles_at_date(date) + 1
        new_date = self.start_date
        if self.schedule_type == "Custom":
            new_date = self.start_date + datetime.timedelta(days=cycles)
        elif self.schedule_type == "Monthly":
            new_date = add_months(self.start_date,cycles)
        elif self.schedule_type == "Yearly":
            new_date = add_months(self.start_date,cycles*12)
        return make_aware(datetime.datetime.combine(new_date, datetime.datetime.min.time()))
            
    

class RecurringIncome(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    added_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    schedule_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name="recincomes")

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    if not isinstance(sourcedate, datetime.datetime):
        return datetime.date(year, month, day)
    return datetime.datetime(year, month, day, tzinfo=timezone.get_current_timezone())
