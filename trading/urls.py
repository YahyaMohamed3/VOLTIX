# trading/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'trading'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('markets' , views.markets , name='markets') 
]