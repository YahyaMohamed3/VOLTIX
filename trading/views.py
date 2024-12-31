from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
import requests
from trading.models import PopularAssets
from .utils import fetch_stock_data
import yfinance as yf
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import format_large_number
import pandas as pd

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
        data = fetch_stock_data(ticker)
        stock_name = PopularAssets.objects.get(ticker = ticker).name
        return render(request , "trading/historical.html" , {"data" : data, "stock_name":stock_name , "ticker" : ticker})
    
@login_required
@require_GET
def stock_data(request):
    symbol = request.GET.get('symbol')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not symbol or not start_date or not end_date:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        data['Percent Change'] = data['Close'].pct_change() * 100
        raw_data = {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'close_prices': [round(price, 2) for price in data['Close'].tolist()],
            'percent_changes': [round(change, 2) if not pd.isna(change) else None for change in data['Percent Change'].tolist()],
            'volumes': [format_large_number(volume) for volume in data['Volume'].tolist()]
        }
        return JsonResponse(raw_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
