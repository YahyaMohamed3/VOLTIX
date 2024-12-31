# trading/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'trading'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('assets/simulation/<str:category>/<str:ticker>/' , views.simulation_type , name='simulation_type'),
    path('assets/simulation/historical/<str:category>/<str:ticker>/' , views.historical , name='historical'),
    path('assets' , views.assets , name='assets'),
     # API
    path('api/stock-data/', views.stock_data, name='stock_data'),
]