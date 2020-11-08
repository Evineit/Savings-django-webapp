from datetime import time
import json
from django.test import TestCase, Client
from django.core.paginator import Paginator
from .models import *
from selenium import webdriver
import datetime
from django.utils.timezone import make_aware


# Create your tests here.
class PostTestCase(TestCase):
    def setUp(self):
        # Create users.
        u1 = User.objects.create_user(username="u1", email="u1@seidai.com", password="pass1234")
        u2 = User.objects.create_user(username="u2", email="u2@seidai.com", password="pass1234")
        u3 = User.objects.create_user(username="u3", email="u3@seidai.com", password="pass1234")
    
        # Create posts.
        cat_1 = Category.objects.create(name="test")
        acc = Account.objects.create(user=u1, name="default",balance=0)
        
    def test_cat_count(self):
        u = User.objects.get(username="u1")
        self.assertEqual(Category.objects.all().count(), 1)

    def test_cat_name(self):
        self.assertEqual(Category.objects.get().name,"test")
    
    def test_rec_payment_cycles_daily(self):
        rec_payment = RecurringPayment.objects.create(
            account = Account.objects.get(),
            description = "test",
            category = Category.objects.get(),
            amount = 10,
            start_date = datetime.date(2020,11,1),
            end_date = datetime.date(2021,11,1),
            schedule_type = "Custom"
        )
        cycles = rec_payment.cycles_at_date(datetime.date(2020,11,11))
        self.assertEqual(cycles,10)

    def test_rec_payment_cycles_monthly(self):
        rec_payment = RecurringPayment.objects.create(
            account = Account.objects.get(),
            description = "test",
            category = Category.objects.get(),
            amount = 10,
            start_date = datetime.date(2020,11,1),
            # end_date = datetime.date(2021,11,1),
            schedule_type = "Monthly"
        )
        cycles = rec_payment.cycles_at_date(datetime.date(2020,11,11))
        self.assertEqual(cycles,0)
        cycles = rec_payment.cycles_at_date(datetime.date(2020,12,1))
        self.assertEqual(cycles,1)
        cycles = rec_payment.cycles_at_date(datetime.date(2021,11,1))
        self.assertEqual(cycles,12)



    def test_rec_payment_create_child(self):
        test = RecurringPayment.objects.create(
            account = Account.objects.get(),
            description = "test",
            category = Category.objects.get(),
            amount = 10,
            start_date = datetime.date(2020,11,1),
            schedule_type = "Custom"
        )
        self.assertEqual(test.expenses.all().count(), 0)
        self.assertEqual(Expense.objects.filter(recurring_parent=test).count(), 0)
        exp = Expense.objects.create(
                account= test.account,
                amount = test.amount,
                added_date = make_aware(datetime.datetime(2020,11,1)),
                category = test.category,
                recurring_parent = test
        )
        self.assertEqual(test.expenses.all().count(), 1)
        self.assertEqual(Expense.objects.filter(recurring_parent=test).count(), 1)
    
    def test_rec_payment_cycles_daily(self):
        test = RecurringPayment.objects.create(
            account = Account.objects.get(),
            description = "test",
            category = Category.objects.get(),
            amount = 10,
            start_date = datetime.datetime(2020,11,1,tzinfo=timezone.get_current_timezone()),
            schedule_type = "Custom"
        )
        self.assertEqual(test.expenses.all().count(), 0)
        test.update_childs()
        self.assertEqual(test.start_date,test.expenses.order_by("added_date").first().added_date)
        self.assertEqual(test.expenses.all().count(),8)
        test.update_childs(datetime.datetime(2020,12,1,tzinfo=timezone.get_current_timezone()))
        # print(test.expenses.all().last())
        self.assertEqual(test.expenses.all().count(),31)
        
    
    def test_rec_payment_cycles_month(self):
        rec_payment = RecurringPayment.objects.create(
            account = Account.objects.get(),
            description = "test",
            category = Category.objects.get(),
            amount = 10,
            start_date = datetime.date(2020,11,1),
            schedule_type = "Monthly"
        )
        self.assertEqual(rec_payment.expenses.all().count(), 0)
        rec_payment.update_childs(datetime.date(2020,11,30))
        self.assertEqual(rec_payment.expenses.all().count(),1)
        rec_payment.update_childs(datetime.date(2020,12,1))
        self.assertEqual(rec_payment.expenses.all().count(),2)
        rec_payment.update_childs(datetime.date(2021,11,1))
        self.assertEqual(rec_payment.expenses.all().count(),13)
        test_date = rec_payment.start_date
        # print(rec_payment.expenses.all())
        for exp in rec_payment.expenses.all():
            self.assertEqual(exp.added_date.date(), test_date)
            test_date = add_months(test_date, 1)



