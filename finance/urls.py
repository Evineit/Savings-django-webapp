from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("accounts",views.account, name="account"),
    # TODO Fix adding spaced accounts
    # - Accounts with number name fail to get all rec payments 
    path("accounts/<str:account>",views.accounts, name="account"),
    path("recpayments/<int:id>",views.rec_payment, name="rec_payment"),
    path("recpayments/<str:account_name>",views.all_rec_payments, name="all_rec_payments"),
]