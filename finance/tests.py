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
    @classmethod
    def setUpTestData(cls):
        cls.u1 = User.objects.create_user(username="u1", email="u1@seidai.com", password="pass1234")
        cls.account_1 = Account.objects.create(user=cls.u1, name="default", balance=0)

    
    def setUp(self):
        self.client = Client()


    def test_server_login(self):
        logged_in = self.client.login(username='u1', password="pass1234")
        self.assertTrue(logged_in)


    def test_server_redirect_if_login_required(self):
        response = self.client.post('/accounts', data={
            'title': 'new_wallet',
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 302)


    def test_server_create_wallet(self):
        self.client.force_login(self.u1)
        response = self.client.post('/accounts', data={
            'title': 'new_wallet',
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = self.client.get(f'/accounts/{response.json().get("id")}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.json().get("balance")), Decimal(15))

    def test_server_create_expense(self):
        self.client.force_login(self.u1)
        response = self.client.post('/accounts/1/expenses', data={
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_all_exp = self.client.get('/accounts/1/expenses')
        self.assertEqual(len(response_all_exp.json()), 1)

    def test_server_create_income(self):
        self.client.force_login(self.u1)
        response = self.client.post('/accounts/1/incomes', data={
            'amount': '15',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_all_inc = self.client.get('/accounts/1/incomes')
        self.assertEqual(len(response_all_inc.json()), 1)

    def test_rec_payment_cycles_monthly(self):
        rec_payment = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 11, 1),
            schedule_type="Monthly"
        )
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 11, 11)))
        self.assertEqual(cycles, 0)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 12, 1)))
        self.assertEqual(cycles, 1)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2021, 11, 1)))
        self.assertEqual(cycles, 12)

    def test_rec_incomes_cycles_monthly(self):
        rec_payment = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 11, 1),
            schedule_type="Monthly"
        )
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 11, 11)))
        self.assertEqual(cycles, 0)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2020, 12, 1)))
        self.assertEqual(cycles, 1)
        cycles = rec_payment.cycles_at_date(make_aware(datetime.datetime(2021, 11, 1)))
        self.assertEqual(cycles, 12)

    def test_rec_payment_create_child(self):
        recurring_payment = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 11, 1),
            schedule_type="Custom"
        )
        Expense.objects.create(
            account=recurring_payment.account,
            amount=recurring_payment.amount,
            added_date=make_aware(datetime.datetime(2020, 11, 1)),
            recurring_parent=recurring_payment
        )
        self.assertEqual(recurring_payment.children.count(), 1)
        self.assertEqual(Expense.objects.filter(recurring_parent=recurring_payment).count(), 1)

    def test_rec_payment_cycles_daily(self):
        date = datetime.datetime(2020, 11, 1)
        test = self.create_test_recurring_payment_object(
            start_date=date,
            schedule_type="Custom"
        )
        self.assertEqual(test.children.count(), 0)
        test.update_children()
        # Checks if the first payment in the first child is the same as the start date
        self.assertEqual(test.start_date, test.children.order_by("added_date").first().added_date)
        # Given that the schedule is daily, checks the number of children is the same as the
        # difference in days + 1 (the first payment)
        self.assertEqual(test.children.count(), (timezone.now() - make_aware(date)).days + 1)

    def test_rec_payment_children_monthly(self):
        rec_payment = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 11, 1),
            schedule_type="Monthly"
        )
        self.assertEqual(rec_payment.children.count(), 0)
        rec_payment.update_children(datetime.datetime(2020, 11, 30))
        self.assertEqual(rec_payment.children.count(), 1)
        rec_payment.update_children(datetime.datetime(2020, 12, 1))
        self.assertEqual(rec_payment.children.count(), 2)
        rec_payment.update_children(datetime.datetime(2021, 11, 1))
        self.assertEqual(rec_payment.children.count(), 13)

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
        self.assertEqual(rec_payment.children.count(), 0)
        rec_payment.update_children(datetime.datetime(2020, 11, 30))
        self.assertEqual(rec_payment.children.count(), 1)
        rec_payment.update_children(datetime.datetime(2020, 12, 1))
        self.assertEqual(rec_payment.children.count(), 2)
        rec_payment.update_children(datetime.datetime(2021, 11, 1))
        self.assertEqual(rec_payment.children.count(), 13)

        test_date = rec_payment.start_date
        for exp in rec_payment.children.all():
            self.assertEqual(exp.added_date.date(), test_date.date())
            test_date = add_months(test_date, 1)

    def test_server_fail_missing_data_recurring_payments(self):
        self.client.force_login(self.u1)
        response: JsonResponse = self.client.post(f'/accounts/{self.account_1.id}', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_server_fail_missing_data_recurring_incomes(self):
        self.client.force_login(self.u1)
        response: JsonResponse = self.client.post(f'/accounts/{self.account_1.id}/recincomes', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_server_recurring_payments(self):
        self.client.force_login(self.u1)
        response = self.client.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_2 = self.client.get('/accounts/1')
        response_3 = self.client.get('/accounts/1/recpayments')
        self.assertEqual(response.status_code, 201)
        self.assertLess(Decimal(response_2.json().get('balance')), 0)
        self.assertEqual(response_3.status_code, 200)

    def test_server_post_new_recurring_income(self):
        self.client.force_login(self.u1)
        response_create = self.client.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_account = self.client.get('/accounts/1')
        response_active_rec_incomes = self.client.get('/accounts/1/recincomes')
        self.assertEqual(response_create.status_code, 201)
        self.assertEqual(response_account.status_code, 200)
        self.assertGreaterEqual(Decimal(response_account.json().get('balance')), 0)
        self.assertEqual(response_active_rec_incomes.status_code, 200)
        self.assertEqual(len(response_active_rec_incomes.json()), 1)

    def test_server_recurring_payments_get_actives(self):
        self.client.force_login(self.u1)
        rec_payment_active = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            schedule_type="Monthly"
        )
        rec_payment_inactive = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            end_date=datetime.datetime(2020, 10, 1),
            schedule_type="Monthly"
        )
        response_payments = self.client.get('/accounts/1/recpayments')
        # Assert only 1 RecurringPayment is active
        self.assertEqual(response_payments.status_code, 200)
        self.assertEqual(len(response_payments.json()), 1)
        # Updates the children at the time
        self.client.get('/accounts/1')
        self.assertGreaterEqual(rec_payment_active.children.count(), 3)
        self.assertEqual(rec_payment_inactive.children.count(), 2)
        rec_payment_active = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            end_date=datetime.datetime(2020, 10, 1),
            schedule_type="Custom"
        )
        rec_payment_active = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            end_date=datetime.datetime(2021, 10, 1),
            schedule_type="Yearly"
        )
        self.client.get('/accounts/default')

    def test_server_recurring_payments_stop(self):
        self.client.force_login(self.u1)
        self.client.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_active_payments = self.client.get('/accounts/1/recpayments')
        self.assertEqual(response_active_payments.status_code, 200)
        self.assertEqual(len(response_active_payments.json()), 1)

        pay_id = response_active_payments.json()[0].get("id")
        rec_pay_response = self.client.get('/recpayments/' + str(pay_id))
        self.assertEqual(rec_pay_response.status_code, 200)
        stop_response = self.client.put(f'/recpayments/{pay_id}/stop', content_type='application/json')
        self.assertEqual(stop_response.status_code, 200)
        response_active_payments = self.client.get('/accounts/1/recpayments')
        self.assertEqual(len(response_active_payments.json()), 0)

    def test_server_recurring_incomes_stop(self):
        self.client.force_login(self.u1)
        self.client.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response_active_incomes = self.client.get('/accounts/1/recincomes')
        self.assertEqual(response_active_incomes.status_code, 200)
        self.assertEqual(len(response_active_incomes.json()), 1)

        pay_id = response_active_incomes.json()[0].get("id")
        rec_pay_response = self.client.get(f'/recincomes/{str(pay_id)}')
        self.assertEqual(rec_pay_response.status_code, 200)
        stop_response = self.client.put(f'/recincomes/{pay_id}/stop', content_type='application/json')
        self.assertEqual(stop_response.status_code, 200)
        response_active_incomes = self.client.get('/accounts/1/recincomes')
        self.assertEqual(len(response_active_incomes.json()), 0)

    def test_server_recurring_payment_next_payment_date(self):
        rec_payment_1 = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 10, 1),
            end_date=datetime.datetime(2020, 11, 1),
            schedule_type="Custom"
        )
        rec_payment_2 = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            end_date=datetime.datetime(2020, 11, 1),
            schedule_type="Monthly"
        )
        rec_payment_3 = self.create_test_recurring_payment_object(
            start_date=datetime.datetime(2020, 9, 1),
            end_date=datetime.datetime(2021, 11, 1),
            schedule_type="Yearly"
        )
        self.assertEqual(rec_payment_1.next_payment_date().date(), datetime.date(2020, 11, 2))
        self.assertEqual(rec_payment_2.next_payment_date().date(), datetime.date(2020, 12, 1))
        self.assertEqual(rec_payment_3.next_payment_date().date(), datetime.date(2021, 9, 1))

    def test_server_recurring_payments_change_amount(self):
        self.client.force_login(self.u1)
        self.client.post('/accounts/1/recpayments', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = self.client.get('/accounts/1/recpayments')
        self.assertEqual(response.status_code, 200)
        pay_id = response.json()[0].get("id")
        change_amount_response = self.client.put(f'/recpayments/{pay_id}/edit', data={
            'amount': 100
        }, content_type='application/json')
        self.assertEqual(change_amount_response.status_code, 200)
        rec_pay_response = self.client.get('/recpayments/' + str(pay_id))
        self.assertEqual(rec_pay_response.status_code, 200)
        self.assertEqual(Decimal(rec_pay_response.json().get('amount')), Decimal(100))
        rec_payment_1 = RecurringPayment.objects.get(pk=pay_id)
        rec_payment_1.update_children(timezone.now() + timezone.timedelta(days=1))
        child_last = rec_payment_1.children.order_by("-id")[0]
        other_child = rec_payment_1.children.order_by("-id")[1]
        self.assertEqual(Decimal(child_last.amount), Decimal(100))
        self.assertEqual(Decimal(other_child.amount), Decimal(15))

    def test_server_recurring_incomes_change_amount(self):
        self.client.force_login(self.u1)
        add_response = self.client.post('/accounts/1/recincomes', data={
            'amount': '15',
            'description': 'test',
            'start_date': '2020-11-01',
            'schedule_type': 'Custom'
        }, content_type='application/json')
        response = self.client.get('/accounts/1/recincomes')
        self.assertEqual(add_response.status_code, 201)
        self.assertEqual(response.status_code, 200)
        pay_id = response.json()[0].get("id")
        change_amount_response = self.client.put(f'/recincomes/{pay_id}/edit', data={
            'amount': 100
        }, content_type='application/json')
        self.assertEqual(change_amount_response.status_code, 200)
        rec_pay_response = self.client.get(f'/recincomes/{pay_id}')
        self.assertEqual(rec_pay_response.status_code, 200)
        self.assertEqual(Decimal(rec_pay_response.json().get('amount')), Decimal(100))
        rec_payment_1 = RecurringIncome.objects.get(pk=pay_id)
        rec_payment_1.update_children(timezone.now() + timezone.timedelta(days=1))
        child_last = rec_payment_1.children.order_by("-id")[0]
        other_child = rec_payment_1.children.order_by("-id")[1]
        self.assertEqual(Decimal(child_last.amount), Decimal(100))
        self.assertEqual(Decimal(other_child.amount), Decimal(15))

    
    def create_test_recurring_payment_object(self,start_date, schedule_type, end_date=None):
        return RecurringPayment.objects.create(
            account=self.account_1,
            description="test",
            amount=10,
            start_date=make_aware(start_date),
            end_date=make_aware(end_date) if end_date else end_date,
            schedule_type=schedule_type
        )
