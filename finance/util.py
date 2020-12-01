import datetime
from datetime import date, time
from django.contrib.auth.models import AbstractUser
from django.db import models
import calendar
from django.utils import timezone
from django.utils.timezone import make_aware

def next_payment_date(recurringObject, date= timezone.now()) -> datetime.datetime:
        cycles = recurringObject.cycles_at_date(date) + 1
        new_date = recurringObject.start_date
        if recurringObject.schedule_type == "Custom":
            new_date = recurringObject.start_date + datetime.timedelta(days=cycles)
        elif recurringObject.schedule_type == "Monthly":
            new_date = add_months(recurringObject.start_date,cycles)
        elif recurringObject.schedule_type == "Yearly":
            new_date = add_months(recurringObject.start_date,cycles*12)
        return make_aware(datetime.datetime.combine(new_date, datetime.datetime.min.time()))

def update_children(recurringObject,childClass,date = timezone.now()):
        cycles = recurringObject.cycles_at_date(date) 
        children_count = recurringObject.children.all().count()
        new_date = recurringObject.start_date
        
        while (children_count <= cycles ):
            if recurringObject.schedule_type == "Custom":
                new_date = recurringObject.start_date + datetime.timedelta(days=children_count)
            elif recurringObject.schedule_type == "Monthly":
                new_date = add_months(recurringObject.start_date,children_count)
            elif recurringObject.schedule_type == "Yearly":
                new_date = add_months(recurringObject.start_date,children_count*12)
            childClass.objects.create(
                    account= recurringObject.account,
                    amount = recurringObject.amount,
                    added_date = make_aware(datetime.datetime.combine(new_date, datetime.datetime.min.time())),
                    recurring_parent = recurringObject
            ) 
            children_count = recurringObject.children.all().count()

def cycles_at_date(recurringObject, date:datetime = timezone.now()) -> int:
        if timezone.is_naive(date): date = make_aware(date)
        if recurringObject.schedule_type == "Custom":
            if recurringObject.end_date and date > recurringObject.end_date:
                delta = recurringObject.end_date - recurringObject.start_date
                return delta.days
            delta = date - recurringObject.start_date
            return delta.days
        elif recurringObject.schedule_type == "Monthly":
            counter = 0
            new_date = recurringObject.start_date
            while new_date < date:
                new_date = add_months(new_date,1)
                if recurringObject.end_date and new_date > recurringObject.end_date:
                    break
                if new_date > date:
                    break
                elif new_date <= date:
                    counter += 1
            return counter
        elif recurringObject.schedule_type == "Yearly":
            counter = 0
            new_date = recurringObject.start_date
            while new_date < date:
                new_date = add_months(new_date,12)
                if recurringObject.end_date and new_date > recurringObject.end_date:
                    break
                if new_date > date:
                    break
                elif new_date <= date:
                    counter += 1
            return counter

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    if not isinstance(sourcedate, datetime.datetime):
        return datetime.date(year, month, day)
    return datetime.datetime(year, month, day, tzinfo=timezone.get_current_timezone())