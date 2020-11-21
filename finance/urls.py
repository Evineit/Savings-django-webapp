from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("accounts",views.account, name="account"),
    path("accounts/<str:account>",views.accounts, name="accounts"),
    path("accounts/<str:account>/recpayments",views.all_rec_payments, name="all_rec_payments"),
    path("accounts/<str:account>/recincomes",views.all_rec_incomes, name="all_rec_incomes"),
    path("recpayments/<int:id>",views.rec_payment, name="rec_payment"),
]