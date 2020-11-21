import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError

from decimal import Decimal

from django.utils.timezone import activate
from .models import *
from datetime import datetime

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

def account(request):
    user = request.user
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Empty POST request"}, status=400)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        title = data.get('title')
        amount = Decimal(data.get("amount"))
        if not title or amount==None:return JsonResponse({"error": "Request info incomplete or missing"}, status=400)
        new_acc = Account.objects.create(user=user,balance=0, name=title)
        category = Category.objects.get(name="Default")
        Income.objects.create(account=new_acc,amount=amount,category=category)
        return JsonResponse({
                    "msg": "Account (wallet) added successfully"
            }, status=201)
    elif request.method == "GET":
        return JsonResponse({"error": "TODO."}, status=400)
    else:
        return JsonResponse({"error": "POST or GET request required."}, status=400)


def accounts(request, account):
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
                    "msg": "Income added successfully"
            }, status=201)
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
                    "msg": "Expense added successfully"
            }, status=201)
        elif request_type == "rec_expense":
            user_account = user.accounts.get(name=account)
            amount = Decimal(data.get("amount"))
            category_name = data.get("category","Default")
            description = data.get("description","No description")
            str_date = data.get("start_date")
            start_date = datetime.strptime(str_date, r'%Y-%m-%d')
            schedule_type = data.get("schedule_type")
            try:
                category = Category.objects.get(name=category_name)
            except:
                return JsonResponse({"error": f"Category: {category_name}. Doesn't exist"}, status=400)
            new_expense = RecurringPayment.objects.create(
                account=user_account,
                description=description,
                amount=amount,
                start_date=make_aware(start_date),
                schedule_type=schedule_type,
                category=category,
            )
            new_expense.update_children()
            user_account.update_balance()
            balance = user_account.balance
            return JsonResponse({
                    "sub": new_expense.serialize(),
                    "msg": "Subscription added successfully"
            }, status=201)
    elif request.method == "GET":
        user_account = user.accounts.get(name=account)
        user_account.update_balance()
        balance = user_account.balance
        return JsonResponse({
            "balance": balance
        }, status=200)
    else:
        return JsonResponse({"error": "POST or GET request required."}, status=400)
        
def all_rec_payments(request, account):
    user = request.user
    if request.method == "GET":
        try:
            account = user.accounts.get(name=account)
            payments = account.rec_expenses.order_by("-id").exclude(end_date__lte=timezone.now()).all()
        except:
            return JsonResponse({"error": f"Account: {account}. Doesn't exist"}, status=400)
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)    
    else:
        return JsonResponse({"error": "GET request required."}, status=400)

def all_rec_incomes(request, account):
    user = request.user
    if request.method == "GET":
        try:
            account = user.accounts.get(name=account)
            payments = account.rec_incomes.order_by("-id").exclude(end_date__lte=timezone.now()).all()
        except:
            return JsonResponse({"error": f"Account: {account}. Doesn't exist"}, status=400)
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)   
    elif request.method == "POST":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        user_account = user.accounts.get(name=account)
        amount = Decimal(data.get("amount"))
        category_name = data.get("category","Default")
        description = data.get("description","No description")
        str_date = data.get("start_date")
        start_date = datetime.strptime(str_date, r'%Y-%m-%d')
        schedule_type = data.get("schedule_type")
        try:
            category = Category.objects.get(name=category_name)
        except:
            return JsonResponse({"error": f"Category: {category_name}. Doesn't exist"}, status=400)
        new_income = RecurringIncome.objects.create(
            account=user_account,
            description=description,
            amount=amount,
            start_date=make_aware(start_date),
            schedule_type=schedule_type,
            category=category,
        )
        new_income.update_children()
        user_account.update_balance()
        return JsonResponse({
                "sub": new_income.serialize(),
                "msg": "New recurrent income added successfully"
        }, status=201) 
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400)

def rec_payment(request, id):
    try:
            payment = RecurringPayment.objects.get(id=id)
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "GET":
        return JsonResponse(payment.serialize(), safe=False, status=200 ) 
    elif request.method == "PUT":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty PUT request"}, status=400)
        action = data.get("action")
        if not action: return JsonResponse({"error": "No action in request"}, status=400)

        if action == "stop":
            payment.end_date = timezone.now()
            payment.save()
            return JsonResponse({"msg": f"Payment with id: {id}. Has been stopped"}, status=200)
        elif action == "change_amount":
            new_amount = data.get("amount")
            if not new_amount: return JsonResponse({"error": "No amount in request"}, status=400)
            payment.amount =  new_amount
            payment.save()
            payment.refresh_from_db()
            return JsonResponse({
                "msg": f"Payment with id: {id}. Has a new amount{new_amount}",
                "amount": payment.amount
            }, status=200)
        else: 
            return JsonResponse({"error":f"Action:{action} doesn't exist"}, status=400) 
    else:
        return JsonResponse({"error": "GET or PUT request required."}, status=400)

def rec_income(request, id):
    try:
            payment = RecurringIncome.objects.get(id=id)
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "GET":
        return JsonResponse(payment.serialize(), safe=False, status=200 ) 
    else:
        return JsonResponse({"error": "GET request required."}, status=400)

def rec_income_stop(request,id):
    try:
            payment = RecurringIncome.objects.get(id=id)
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "PUT":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty PUT request"}, status=400)  
        payment.end_date = timezone.now()
        payment.save()
        return JsonResponse({"msg": f"Payment with id: {id}. Has been stopped"}, status=200)

def rec_income_edit(request,id):
    try:
            payment = RecurringIncome.objects.get(id=id)
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "PUT":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty PUT request"}, status=400)
        new_amount = data.get("amount")
        if not new_amount: return JsonResponse({"error": "No amount in request"}, status=400)
        payment.amount =  new_amount
        payment.save()
        payment.refresh_from_db()
        return JsonResponse({
            "msg": f"Payment with id: {id}. Has a new amount{new_amount}",
            "amount": payment.amount
        }, status=200)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


        