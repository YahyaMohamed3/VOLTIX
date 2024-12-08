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
def markets(request):
    return render(request , "trading/markets.html")

@login_required
def assets(request):
    popular_assets = PopularAssets.objects.all()
    print(popular_assets)
    return render(request , "trading/assets.html" , {"popular_assets": popular_assets})