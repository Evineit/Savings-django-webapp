from django.contrib import admin
from .models import User, Account, Income, Expense, RecurringIncome, RecurringPayment

# Register your models here.
admin.site.register(User)
admin.site.register(Account)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(RecurringIncome)
admin.site.register(RecurringPayment)
