from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("accounts",views.account, name="account"),
    path("accounts/<int:account_id>",views.accounts, name="accounts"),
    path("accounts/<int:account_id>/delete",views.accounts_delete, name="accounts_delete"),
    path("accounts/<int:account_id>/incomes",views.all_incomes, name="all_incomes"),
    path("accounts/<int:account_id>/expenses",views.all_expenses, name="all_expenses"),
    path("accounts/<int:account_id>/recpayments",views.all_rec_payments, name="all_rec_payments"),
    path("accounts/<int:account_id>/recincomes",views.all_rec_incomes, name="all_rec_incomes"),
    path("recpayments/<int:id>",views.rec_payment, name="rec_payment"),
    path("recincomes/<int:id>",views.rec_income, name="rec_income"),
    path("recincomes/<int:id>/stop",views.rec_income_stop, name="rec_income_stop"),
    path("recincomes/<int:id>/edit",views.rec_income_edit, name="rec_income_edit"),
]