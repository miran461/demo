from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()   

class FinancialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_accounts', verbose_name='Account Owner')
    account_type = models.CharField(max_length=255, verbose_name='Account Type')
    account_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Account Number', help_text='The unique identifier for the account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], verbose_name='Balance')
    is_negative = models.BooleanField(default=False, verbose_name='Is Negative Balance?', help_text='Check if the balance is negative')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Last Updated')
    
    
    class Meta:
        verbose_name = 'Financial Account'
        verbose_name_plural = 'Financial Accounts'
        # ordering = ['account_type', 'account_name']

    def __str__(self):
        name = f"{self.user.username} - {self.account_type}"
        if self.account_number:
            name = f"{name}-{self.account_number}"
        return f"{name}*" if self.account_number else name

    def display_balance(self):
        """Returns formatted balance with currency symbol and proper sign"""
        amount = f"${abs(self.balance):,.2f}"
        return f"-{amount}" if self.is_negative else amount

    @property
    def actual_balance(self):
        """Returns the signed balance value"""
        return -self.balance if self.is_negative else self.balance
    
    
    @classmethod
    def get_all_totals(cls, user=None):
        """Returns system total, all user totals, and optionally a specific user's total"""
        from django.db.models import Sum, Case, When, F, DecimalField
        from decimal import Decimal
        
        queryset = cls.objects.annotate(
            actual_balance=Case(
                When(is_negative=True, then=-F('balance')),
                default=F('balance'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
        
        result = {
            'system_total': queryset.aggregate(
                Sum('actual_balance')
            )['actual_balance__sum'] or Decimal('0.00'),
            'user_totals': queryset.values('user__username').annotate(
                total=Sum('actual_balance')
            ).order_by('user__username')
        }
        
        if user:
            result['user_total'] = queryset.filter(user=user).aggregate(
                Sum('actual_balance')
            )['actual_balance__sum'] or Decimal('0.00')
        
        return result
    

    @classmethod
    def get_all_totals_absolute(cls, user=None):
        """Sum all balances as absolute values and return formatted strings"""
        from django.db.models import Sum, F
        from decimal import Decimal
        
        queryset = cls.objects.annotate(
            absolute_balance=F('balance')  # Use raw balance (ignore is_negative)
        )
        
        # Get raw totals first
        system_total = queryset.aggregate(
            Sum('absolute_balance')
        )['absolute_balance__sum'] or Decimal('0.00')
        
        user_totals = queryset.values('user__username').annotate(
            total=Sum('absolute_balance')
        ).order_by('user__username')
        
        # Format the results
        result = {
            'system_total': f"${system_total:,.2f}",
            'user_totals': [
                {
                    'username': item['user__username'],
                    'total': f"${item['total']:,.2f}"  # Format each user's total
                }
                for item in user_totals
            ]
        }
        
        if user:
            user_total = queryset.filter(user=user).aggregate(
                Sum('absolute_balance')
            )['absolute_balance__sum'] or Decimal('0.00')
            result['user_total'] = f"${user_total:,.2f}"
        
        return result