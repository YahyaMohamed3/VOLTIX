from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
import requests


@login_required
def dashboard(request):
    return render(request , "trading/dashboard.html")


@login_required 
def markets(request):
    return render(request , "markets.html")
