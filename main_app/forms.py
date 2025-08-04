from django import forms
from django.contrib.auth import get_user_model
from .models import FinancialAccount

User = get_user_model()

class FinancialAccountForm(forms.ModelForm):
    class Meta:
        model = FinancialAccount
        fields = ['account_type', 'account_number', 'balance']
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.is_admin = kwargs.pop('is_admin', False)
        super().__init__(*args, **kwargs)
        
        if self.is_admin:
            self.fields['user'] = forms.ModelChoiceField(
                queryset=User.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            self.fields['user'].label = "Account Owner"
            self.fields['user'].required = True