"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main_app import views

urlpatterns = [
    # path("accounts/", include("django.contrib.auth.urls")),
    path('the_boss/', admin.site.urls, name='the-boss'),
    path('', views.user_login, name='user_login'),
    path('logout', views.custom_logout, name='logout'),
    path('my-account/', views.UserAccountDetailView.as_view(), name='user-account-detail'),
    
    path('protected/', views.ProtectedView.as_view(), name='protected-page'),
    path('permission-denied/', views.permission_denied_alert, name='permission-denied-alert'),
]

