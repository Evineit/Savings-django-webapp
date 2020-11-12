from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    path("accounts/<str:account>",views.account, name="account"),
    path("recpayments/<str:account_name>",views.all_rec_payments, name="all_rec_payments"),
]