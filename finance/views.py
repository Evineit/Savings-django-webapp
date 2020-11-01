import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError

from decimal import Decimal
from .models import *

# Create your views here. 
def index(request):
    if (request.user.is_authenticated):
        if (not request.user.accounts.all().count()):
            default_account = Account(user = request.user,balance=0,name="Default")
            default_account.save()
        default_account = request.user.accounts.get(name="Default")
        return render(request, "finance/index.html",{
            "account":default_account
        })
    return render(request, "finance/index.html")
    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "finance/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "finance/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "finance/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            # default_account = Account(user=user,balance=0,name="Default")
            # default_account.save()
        except IntegrityError:
            return render(request, "finance/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "finance/register.html")

def account(request, account):
    user = request.user
    if request.method == "POST":
        data = json.loads(request.body)
        if not data:
            return JsonResponse({"error": "Empty POST request"}, status=400)
        if not data.get("type"):
            return JsonResponse({"error": "No type in request"}, status=400)
        request_type = data.get("type")
        if request_type == "income":
            user_account = user.accounts.get(name=account)
            amount = Decimal(data.get("amount"))
            category_name = data.get("category","Default")
            try:
                category = Category.objects.get(name=category_name)
            except:
                return JsonResponse({"error": f"Category: {category_name}. Doesn't exist"}, status=400)
            new_income = Income(account=user_account, amount=amount, category=category)
            balance = user_account.balance
            new_income.save()
            user_account.update_balance()
            balance = user_account.balance
            return JsonResponse({
                    "account": account,
                    "payment_amount": amount,
                    "new balance": balance,
                    "msg": "Income added succesfully"
            }, status=200)
        elif request_type == "expense":
            user_account = user.accounts.get(name=account)
            amount = Decimal(data.get("amount"))
            category_name = data.get("category","Default")
            try:
                category = Category.objects.get(name=category_name)
            except:
                return JsonResponse({"error": f"Category: {category_name}. Doesn't exist"}, status=400)
            new_expense = Expense(account=user_account, amount=amount, category=category)
            balance = user_account.balance
            new_expense.save()
            user_account.update_balance()
            balance = user_account.balance
            return JsonResponse({
                    "account": account,
                    "payment_amount": amount,
                    "new balance": balance,
                    "msg": "Expense added succesfully"
            }, status=200)
    elif request.method == "GET":
        user_account = user.accounts.get(name=account)
        user_account.update_balance()
        balance = user_account.balance
        return JsonResponse({
            "balance": balance
        }, status=201)
        pass
    else:
        return JsonResponse({"error": "POST or GET request required."}, status=400)
        
