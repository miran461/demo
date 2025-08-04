from django.contrib import admin

# Register your models here.
from .models import FinancialAccount

admin.site.register(FinancialAccount)