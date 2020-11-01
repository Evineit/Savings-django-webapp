from django import forms
from django.core.exceptions import ValidationError
from .models import *



class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount']

    # def clean(self):
    #     data = super().clean()
    #     instance = self.instance
    #     if instance and data["amount"] <= instance.auction.get_price():
    #         raise ValidationError("Bid must be bigger than actual price")
