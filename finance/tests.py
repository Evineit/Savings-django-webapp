import datetime
from decimal import Decimal

from django.http.response import JsonResponse
from django.test import TestCase, Client
from django.utils import timezone
from django.utils.timezone import make_aware

from .models import User, Account, Expense, RecurringIncome, RecurringPayment
from .util import add_months


# Create your tests here.

class PostTestCase(TestCase):
    def setUp(self):
        # Create users.
        u1 = User.objects.create_user(username="u1", email="u1@seidai.com", password="pass1234")
        # u2 = User.objects.create_user(username="u2", email="u2@seidai.com", password="pass1234")
        # u3 = User.objects.create_user(username="u3", email="u3@seidai.com", password="pass1234")

        # Create posts.
        Account.objects.create(user=u1, name="default", balance=0)

    def test_server_account_name(self):
        u1 = User.objects.get(username="u1")
        acc = Account.objects.create(user=u1, name="123", balance=0)
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response = c.get(f'/accounts/{acc.id}/recpayments')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_server_create_wallet(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response = c.post('/accounts', data={
            'title': 'new_wallet',
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = c.get(f'/accounts/{response.json().get("id")}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.json().get("balance")), Decimal(15))

    def test_server_create_expense(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response_all_exp = c.get('/accounts/1/expenses')
        self.assertEqual(len(response_all_exp.json()), 0)
        response = c.post('/accounts/1/expenses', data={
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_all_exp = c.get('/accounts/1/expenses')
        self.assertEqual(len(response_all_exp.json()), 1)

    def test_server_create_income(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response_all_inc = c.get('/accounts/1/incomes')
        self.assertEqual(len(response_all_inc.json()), 0)
        response = c.post('/accounts/1/incomes', data={
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_all_inc = c.get('/accounts/1/incomes')
        self.assertEqual(len(response_all_inc.json()), 1)

    def test_rec_payment_cycles_monthly(self):
        rec_payment = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Monthly"
        )
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 11, 11)))
        self.assertEqual(cycles, 0)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 12, 1)))
        self.assertEqual(cycles, 1)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2021, 11, 1)))
        self.assertEqual(cycles, 12)

    def test_rec_incomes_cycles_monthly(self):
        rec_payment = RecurringIncome.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Monthly"
        )
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 11, 11)))
        self.assertEqual(cycles, 0)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 12, 1)))
        self.assertEqual(cycles, 1)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2021, 11, 1)))
        self.assertEqual(cycles, 12)

    def test_rec_payment_create_child(self):
        test = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Custom"
        )
        self.assertEqual(test.children.all().count(), 0)
        self.assertEqual(Expense.objects.filter(recurring_parent=test).count(), 0)
        Expense.objects.create(
            account=test.account,
            amount=test.amount,
            added_date=make_aware(datetime.datetime(2020, 11, 1)),
            recurring_parent=test
        )
        self.assertEqual(test.children.all().count(), 1)
        self.assertEqual(Expense.objects.filter(recurring_parent=test).count(), 1)

    def test_rec_payment_cycles_daily(self):
        date = datetime.datetime(2020, 11, 1, tzinfo=timezone.get_current_timezone())
        test = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=date,
            schedule_type="Custom"
        )
        self.assertEqual(test.children.all().count(), 0)
        test.update_children()
        # Checks if the first payment in the first child is the same as the start date
        self.assertEqual(test.start_date, test.children.order_by("added_date").first().added_date)
        # Given that the schedule is daily, checks the number of children is the same as the
        # difference in days + 1 (the first payment)
        self.assertEqual(test.children.all().count(), (timezone.now() - date).days + 1)

    def test_rec_payment_children_monthly(self):
        rec_payment = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Monthly"
        )
        self.assertEqual(rec_payment.children.all().count(), 0)
        rec_payment.update_children(datetime.datetime(2020, 11, 30))
        self.assertEqual(rec_payment.children.all().count(), 1)
        rec_payment.update_children(datetime.datetime(2020, 12, 1))
        self.assertEqual(rec_payment.children.all().count(), 2)
        rec_payment.update_children(datetime.datetime(2021, 11, 1))
        self.assertEqual(rec_payment.children.all().count(), 13)

        test_date = rec_payment.start_date
        for exp in rec_payment.children.all():
            self.assertEqual(exp.added_date.date(), test_date.date())
            test_date = add_months(test_date, 1)

    def test_rec_income_children_monthly(self):
        rec_payment = RecurringIncome.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Monthly"
        )
        self.assertEqual(rec_payment.children.all().count(), 0)
        rec_payment.update_children(datetime.datetime(2020, 11, 30))
        self.assertEqual(rec_payment.children.all().count(), 1)
        rec_payment.update_children(datetime.datetime(2020, 12, 1))
        self.assertEqual(rec_payment.children.all().count(), 2)
        rec_payment.update_children(datetime.datetime(2021, 11, 1))
        self.assertEqual(rec_payment.children.all().count(), 13)

        test_date = rec_payment.start_date
        for exp in rec_payment.children.all():
            self.assertEqual(exp.added_date.date(), test_date.date())
            test_date = add_months(test_date, 1)

    def test_server_fail_recurring_payments(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        account = Account.objects.get()
        response: JsonResponse = c.post(f'/accounts/{account.id}', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_server_fail_recurring_incomes(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        account = Account.objects.get()
        response: JsonResponse = c.post(f'/accounts/{account.id}/recincomes', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_server_recurring_payments(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response = c.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_2 = c.get('/accounts/1')
        response_3 = c.get('/accounts/1/recpayments')
        self.assertEqual(response.status_code, 201)
        self.assertLess(Decimal(response_2.json().get('balance')), 0)
        self.assertEqual(response_3.status_code, 200)

    def test_server_recurring_incomes(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        response = c.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_2 = c.get('/accounts/1')
        response_3 = c.get('/accounts/1/recincomes')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_2.status_code, 200)
        self.assertGreaterEqual(Decimal(response_2.json().get('balance')), 0)
        self.assertEqual(response_3.status_code, 200)

    def test_server_recurring_payments_get_actives(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        rec_payment_active = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            schedule_type="Monthly"
        )
        rec_payment_inactive = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            end_date=make_aware(datetime.datetime(2020, 10, 1)),
            schedule_type="Monthly"
        )
        response_payments = c.get('/accounts/1/recpayments')
        # Assert only 1 RecurringPayment is active
        self.assertEqual(response_payments.status_code, 200)
        self.assertEqual(len(response_payments.json()), 1)
        # Updates the children at the time
        c.get('/accounts/1')
        self.assertGreaterEqual(rec_payment_active.children.count(), 3)
        self.assertEqual(rec_payment_inactive.children.count(), 2)
        rec_payment_active = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            end_date=make_aware(datetime.datetime(2020, 10, 1)),
            schedule_type="Custom"
        )
        rec_payment_active = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            end_date=make_aware(datetime.datetime(2021, 10, 1)),
            schedule_type="Yearly"
        )
        c.get('/accounts/default')

    def test_server_recurring_payments_stop(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        c.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = c.get('/accounts/1/recpayments')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        pay_id = response.json()[0].get("id")
        rec_pay_response = c.get('/recpayments/' + str(pay_id))
        self.assertEqual(rec_pay_response.status_code, 200)
        stop_response = c.put(f'/recpayments/{pay_id}/stop', content_type='application/json')
        self.assertEqual(stop_response.status_code, 200)
        response = c.get('/accounts/1/recpayments')
        self.assertEqual(len(response.json()), 0)

    def test_server_recurring_incomes_stop(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        c.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = c.get('/accounts/1/recincomes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        pay_id = response.json()[0].get("id")
        rec_pay_response = c.get(f'/recincomes/{str(pay_id)}')
        self.assertEqual(rec_pay_response.status_code, 200)
        stop_response = c.put(f'/recincomes/{pay_id}/stop', content_type='application/json')
        self.assertEqual(stop_response.status_code, 200)
        response = c.get('/accounts/1/recincomes')
        self.assertEqual(len(response.json()), 0)

    def test_server_recurring_payment_next_payment_date(self):
        rec_payment_1 = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 10, 1)),
            end_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Custom"
        )
        rec_payment_2 = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            end_date=make_aware(datetime.datetime(2020, 11, 1)),
            schedule_type="Monthly"
        )
        rec_payment_3 = RecurringPayment.objects.create(
            account=Account.objects.get(),
            description="test",
            amount=10,
            start_date=make_aware(datetime.datetime(2020, 9, 1)),
            end_date=make_aware(datetime.datetime(2021, 11, 1)),
            schedule_type="Yearly"
        )
        self.assertEqual(rec_payment_1.next_payment_date().date(), datetime.date(2020, 11, 2))
        self.assertEqual(rec_payment_2.next_payment_date().date(), datetime.date(2020, 12, 1))
        self.assertEqual(rec_payment_3.next_payment_date().date(), datetime.date(2021, 9, 1))

    def test_server_recurring_payments_change_amount(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        c.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = c.get('/accounts/1/recpayments')
        self.assertEqual(response.status_code, 200)
        pay_id = response.json()[0].get("id")
        change_amount_response = c.put(f'/recpayments/{pay_id}/edit', data={
            'amount': 100
        }, content_type='application/json')
        self.assertEqual(change_amount_response.status_code, 200)
        rec_pay_response = c.get('/recpayments/' + str(pay_id))
        self.assertEqual(rec_pay_response.status_code, 200)
        self.assertEqual(Decimal(rec_pay_response.json().get('amount')), Decimal(100))
        rec_payment_1 = RecurringPayment.objects.get(pk=pay_id)
        rec_payment_1.update_children(timezone.now() + timezone.timedelta(days=1))
        child_last = rec_payment_1.children.order_by("-id")[0]
        other_child = rec_payment_1.children.order_by("-id")[1]
        self.assertEqual(Decimal(child_last.amount), Decimal(100))
        self.assertEqual(Decimal(other_child.amount), Decimal(15))

    def test_server_recurring_incomes_change_amount(self):
        c = Client()
        logged_in = c.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)
        add_response = c.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = c.get('/accounts/1/recincomes')
        self.assertEqual(add_response.status_code, 201)
        self.assertEqual(response.status_code, 200)
        pay_id = response.json()[0].get("id")
        change_amount_response = c.put(f'/recincomes/{pay_id}/edit', data={
            'amount': 100
        }, content_type='application/json')
        self.assertEqual(change_amount_response.status_code, 200)
        rec_pay_response = c.get(f'/recincomes/{pay_id}')
        self.assertEqual(rec_pay_response.status_code, 200)
        self.assertEqual(Decimal(rec_pay_response.json().get('amount')), Decimal(100))
        rec_payment_1 = RecurringIncome.objects.get(pk=pay_id)
        rec_payment_1.update_children(timezone.now() + timezone.timedelta(days=1))
        child_last = rec_payment_1.children.order_by("-id")[0]
        other_child = rec_payment_1.children.order_by("-id")[1]
        self.assertEqual(Decimal(child_last.amount), Decimal(100))
        self.assertEqual(Decimal(other_child.amount), Decimal(15))
