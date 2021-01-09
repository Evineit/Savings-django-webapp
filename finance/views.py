import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from decimal import Decimal
from django.core.paginator import Paginator
from django.utils.timezone import activate
from .models import User, Account, Income, Expense, RecurringIncome, RecurringPayment
from datetime import datetime

def index(request):
    if (request.user.is_authenticated):
        if (not request.user.accounts.all().count()):
            default_account = Account(user = request.user,balance=0,name="Default")
            default_account.save()
        default_account = request.user.accounts.first()
        return render(request, "finance/index.html",{
            "account":default_account
        })
    return render(request, "finance/nolog.html")
    

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
        except IntegrityError:
            return render(request, "finance/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "finance/register.html")

@login_required
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
        if amount>0: Income.objects.create(account=new_acc,amount=abs(amount))
        elif amount<0: Expense.objects.create(account=new_acc,amount=abs(amount))
        return JsonResponse({
                    "msg": "Account (wallet) added successfully",
                    "id": new_acc.id
            }, status=201)
    elif request.method == "GET":
        accounts = user.accounts.all()
        return JsonResponse([acc.serialize() for acc in accounts], safe=False, status=200)    
    else:
        return JsonResponse({"error": "POST or GET request required."}, status=400)

@login_required
def accounts_delete(request, account_id):
    user = request.user
    if request.method == "DELETE":
        try:
            user_account = user.accounts.get(pk=account_id)
        except:
            return JsonResponse({"error": "Account doesn't exist"}, status=400)
        user_account.delete()
        return JsonResponse({
                        "msg": "User account removed successfully"
                }, status=200) 
    return JsonResponse({"error": "Delete request required."}, status=400)

@login_required
def accounts(request, account_id):
    user = request.user
    if request.method == "GET":
        user_account = user.accounts.get(pk=account_id)
        user_account.update_balance()
        balance = user_account.balance
        return JsonResponse({
            "balance": balance
        }, status=200)
    else:
        return JsonResponse({"error": "GET request required."}, status=400)

@login_required
def all_incomes(request, account_id):
    user = request.user
    if request.method == "GET":
        try:
            account_id = user.accounts.get(pk=account_id)
            payments = account_id.incomes.order_by("-id").all()
        except:
            return JsonResponse({"error": f"Account: {account_id}. Doesn't exist"}, status=400)
        if request.GET.get('page'):
            page_number = request.GET.get('page')
            paginator = Paginator([payment.serialize() for payment in payments], 10)
            page_obj = paginator.get_page(page_number)
            return JsonResponse(page_obj.object_list, safe=False, status=200)    
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)    
    elif request.method == "POST":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        user_account = user.accounts.get(pk=account_id)
        amount = Decimal(data.get("amount"))
        new_income = Income.objects.create(account=user_account, amount=amount)
        user_account.update_balance()
        new_income.refresh_from_db()
        return JsonResponse({
                "sub": new_income.serialize(),
                "msg": "Income added successfully"
        }, status=201) 
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400) 

@login_required
def all_expenses(request, account_id):
    user = request.user
    if request.method == "GET":
        try:
            account_id = user.accounts.get(pk=account_id)
            payments = account_id.expenses.order_by("-id").all()
        except:
            return JsonResponse({"error": f"Account: {account_id}. Doesn't exist"}, status=400)
        if request.GET.get('page'):
            page_number = request.GET.get('page')
            paginator = Paginator([payment.serialize() for payment in payments], 10)
            page_obj = paginator.get_page(page_number)
            return JsonResponse(page_obj.object_list, safe=False, status=200)   
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)    
    elif request.method == "POST":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        user_account = user.accounts.get(pk=account_id)
        amount = Decimal(data.get("amount"))
        new_expense = Expense.objects.create(account=user_account, amount=amount)
        user_account.update_balance()
        new_expense.refresh_from_db()
        return JsonResponse({
                "sub": new_expense.serialize(),
                "msg": "Expense added successfully"
        }, status=201) 
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400) 

@login_required
def all_rec_payments(request, account_id):
    user = request.user
    if request.method == "GET":
        try:
            account_id = user.accounts.get(pk=account_id)
            payments = account_id.rec_expenses.order_by("-id").exclude(end_date__lte=timezone.now()).all()
        except:
            return JsonResponse({"error": f"Account: {account_id}. Doesn't exist"}, status=400)
        if request.GET.get('page'):
            page_number = request.GET.get('page')
            paginator = Paginator([payment.serialize() for payment in payments], 10)
            page_obj = paginator.get_page(page_number)
            return JsonResponse(page_obj.object_list, safe=False, status=200)   
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)    
    elif request.method == "POST":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        user_account = user.accounts.get(pk=account_id)
        amount = Decimal(data.get("amount"))
        description = data.get("description","No description")
        str_date = data.get("start_date")
        start_date = datetime.strptime(str_date, r'%Y-%m-%d')
        schedule_type = data.get("schedule_type")
        new_expense = RecurringPayment.objects.create(
            account=user_account,
            description=description,
            amount=amount,
            start_date=make_aware(start_date),
            schedule_type=schedule_type,
        )
        new_expense.update_children()
        user_account.update_balance()
        new_expense.refresh_from_db()
        return JsonResponse({
                "sub": new_expense.serialize(),
                "msg": "New Subscription added successfully"
        }, status=201) 
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400)

@login_required
def all_rec_incomes(request, account_id):
    user = request.user
    if request.method == "GET":
        try:
            account_id = user.accounts.get(pk=account_id)
            payments = account_id.rec_incomes.order_by("-id").exclude(end_date__lte=timezone.now()).all()
        except:
            return JsonResponse({"error": f"Account: {account_id}. Doesn't exist"}, status=400)
        if request.GET.get('page'):
            page_number = request.GET.get('page')
            paginator = Paginator([payment.serialize() for payment in payments], 10)
            page_obj = paginator.get_page(page_number)
            return JsonResponse(page_obj.object_list, safe=False, status=200)   
        return JsonResponse([payment.serialize() for payment in payments], safe=False, status=200)   
    elif request.method == "POST":
        data = json.loads(request.body)
        if not data: return JsonResponse({"error": "Empty POST request"}, status=400)
        user_account = user.accounts.get(pk=account_id)
        amount = Decimal(data.get("amount"))
        description = data.get("description","No title")
        str_date = data.get("start_date")
        start_date = datetime.strptime(str_date, r'%Y-%m-%d')
        schedule_type = data.get("schedule_type")
        new_income = RecurringIncome.objects.create(
            account=user_account,
            description=description,
            amount=amount,
            start_date=make_aware(start_date),
            schedule_type=schedule_type,
        )
        new_income.update_children()
        new_income.refresh_from_db()
        user_account.update_balance()
        return JsonResponse({
                "sub": new_income.serialize(),
                "msg": "New recurrent income added successfully"
        }, status=201) 
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400)

@login_required
def rec_payment(request, id):
    user = request.user
    try:
            payment = RecurringPayment.objects.get(id=id)
            if payment.account not in user.accounts.all(): 
                return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "GET":
        return JsonResponse(payment.serialize(), safe=False, status=200 ) 
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def rec_income(request, id):
    user = request.user
    try:
            payment = RecurringIncome.objects.get(id=id)
            if payment.account not in user.accounts.all(): 
                return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "GET":
        return JsonResponse(payment.serialize(), safe=False, status=200 ) 
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def rec_payment_edit(request,id):
    user = request.user
    try:
        payment = RecurringPayment.objects.get(id=id)
        if payment.account not in user.accounts.all(): 
            return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
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
            "msg": f"Payment with id: {id}. Has a new amount:{new_amount}",
            "amount": payment.amount
        }, status=200)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)

@login_required
def rec_payment_stop(request,id):
    user = request.user
    try:
        payment = RecurringPayment.objects.get(id=id)
        if payment.account not in user.accounts.all(): 
            return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "PUT":
        payment.end_date = timezone.now()
        payment.save()
        return JsonResponse({"msg": f"Payment with id: {id}. Has been stopped"}, status=200)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@login_required
def rec_income_stop(request,id):
    user = request.user
    try:
        payment = RecurringIncome.objects.get(id=id)
        if payment.account not in user.accounts.all(): 
            return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
    except:
            return JsonResponse({"error": f"Payment with id: {id}. Doesn't exist"}, status=400) 
    if request.method == "PUT":
        payment.end_date = timezone.now()
        payment.save()
        return JsonResponse({"msg": f"Payment with id: {id}. Has been stopped"}, status=200)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)

@login_required
def rec_income_edit(request,id):
    user = request.user
    try:
        payment = RecurringIncome.objects.get(id=id)
        if payment.account not in user.accounts.all(): 
            return JsonResponse({"error": f"The user does not have access rights to the payment with id: {id}"}, status=403) 
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


        