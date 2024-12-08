from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
import requests
from trading.models import PopularAssets

@login_required
def dashboard(request):
    return render(request , "trading/dashboard.html")


@login_required 
def simulation_type(request , ticker , category):
    if not ticker and category:
        return redirect("trading:assets")
    return render(request , "trading/simulation_type.html",{"ticker" : ticker ,  "category":category})

@login_required
def assets(request):
    popular_stocks = PopularAssets.objects.filter(category = "stock")
    popular_etfs = PopularAssets.objects.filter(category = "etf")
    return render(request , "trading/assets.html" , {"popular_stocks": popular_stocks , "popular_etfs":popular_etfs})

@login_required
def historical(request , ticker, category):
    if request.method == "GET":
        if not ticker and category:
            return redirect("trading:assets")
        return render(request , "trading/historical.html")
