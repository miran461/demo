from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .models import FinancialAccount


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            if user.is_superuser:
                return redirect('/the_boss')
            return redirect('user-account-detail')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out!")
    return redirect("user_login")




class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to verify user is admin"""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('account-list')

class AccountListView(LoginRequiredMixin, ListView):
    model = FinancialAccount
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        # Regular users see only their accounts, admins see all
        if self.request.user.is_staff:
            return FinancialAccount.objects.all().order_by('user', 'account_type')
        return FinancialAccount.objects.filter(user=self.request.user).order_by('account_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['now'] = timezone.now()
        context['total_assets'] = sum(acc.balance for acc in queryset if not self.request.user.is_staff)
        return context



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Case, When, F, DecimalField
from decimal import Decimal



class UserAccountDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'user_account_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user accounts with actual balance calculation
        accounts = FinancialAccount.objects.filter(user=user).annotate(
            actual_balance=Case(
                When(is_negative=True, then=-F('balance')),
                default=F('balance'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
        
        # Calculate user's total balance
        user_total = accounts.aggregate(
            total=Sum('actual_balance')
        )['total'] or Decimal('0.00')
        
        totals = FinancialAccount.get_all_totals_absolute(user=user)
        
        context.update({
            'user': user,
            'accounts': accounts,
            'total_assets': user_total,
            'accounts': FinancialAccount.objects.filter(user=user),
            'totals': totals
        })
        return context



from django.contrib import messages
from django.shortcuts import redirect

def permission_denied_view(request):
    # Add error message to be displayed in toast
    messages.error(request, "You are not allowed to view this content")
    
    # Get the referring page (current page) or default to home
    redirect_url = request.META.get('HTTP_REFERER', '/')
    
    # Redirect back to the same page
    return redirect(redirect_url)


# class AccountCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
#     model = FinancialAccount
#     form_class = FinancialAccountForm
#     template_name = 'accounts/account_form.html'
#     success_url = reverse_lazy('account-list')
    
#     def form_valid(self, form):
#         form.instance.user = form.cleaned_data.get('user') or self.request.user
#         return super().form_valid(form)
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['is_admin'] = self.request.user.is_staff
#         return kwargs

# class AccountUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
#     model = FinancialAccount
#     form_class = FinancialAccountForm
#     template_name = 'accounts/account_form.html'
#     success_url = reverse_lazy('account-list')
    
#     def get_queryset(self):
#         return FinancialAccount.objects.all()
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['is_admin'] = self.request.user.is_staff
#         return kwargs

# class AccountDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
#     model = FinancialAccount
#     template_name = 'accounts/account_confirm_delete.html'
#     success_url = reverse_lazy('account-list')
    
#     def get_queryset(self):
#         return FinancialAccount.objects.all()




# Permission denied handler view
def permission_denied_alert(request):
    error_msg = "You are not allowed to view this content, contact your account officer to get the problem solved"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'title': 'Oops!',
            'message': error_msg,
            'redirect': request.META.get('HTTP_REFERER', '/')
        })
    
    messages.error(request, error_msg)
    return redirect(request.META.get('HTTP_REFERER', 'user-account-detail'))




class ProtectedView(TemplateView):
    template_name = 'protected_page.html'
    
    def dispatch(self, request, *args, **kwargs):
        messages.error(request, "This page is completely restricted")
        return redirect('permission-denied-alert')