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
import pandas as pd
from datetime import datetime, timedelta
from json import JSONDecodeError
import json 
from .forms import SimulationForm

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
    try:
        symbol = request.GET.get('symbol')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not symbol or not start_date or not end_date:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

        # Try to get reference price by looking back up to 5 trading days
        reference_price = None
        stock = yf.Ticker(symbol)
        for days_back in range(1, 6):
            look_back_date = (start_date_dt - timedelta(days=days_back)).strftime('%Y-%m-%d')
            look_back_end = (start_date_dt - timedelta(days=days_back-1)).strftime('%Y-%m-%d')
            
            prev_day_data = stock.history(start=look_back_date, end=look_back_end)
            
            if not prev_day_data.empty:
                reference_price = prev_day_data['Close'].iloc[-1]
                break

        if reference_price is None:
            return JsonResponse({'error': 'Could not find reference price in the last 5 trading days'}, status=404)

        # Calculate the time period
        time_period = end_date_dt - start_date_dt

        if time_period.days >= 30:
            # Fetch daily data if the time period is a month or longer
            data = stock.history(start=start_date, end=end_date, interval='1d')
            date_format = '%Y-%m-%d'  # Format for daily data
        else:
            # Fetch data at three different times within each day if the time period is less than a month
            data = stock.history(start=start_date, end=end_date, interval='90m')
            date_format = '%Y-%m-%d %H:%M:%S'  # Format for intraday data

        if data.empty:
            return JsonResponse({'error': 'No data available for the specified date range'}, status=404)

        # Calculate percent change based on the reference price
        data['Percent Change'] = ((data['Close'] - reference_price) / reference_price) * 100

        # Prepare the data for JSON response
        raw_data = {
            'dates': data.index.strftime(date_format).tolist(),
            'close_prices': [round(price, 2) for price in data['Close'].tolist()],
            'percent_changes': [round(change, 2) if not pd.isna(change) else None for change in data['Percent Change'].tolist()],
            'volumes': [f"{int(round(volume)):,}" for volume in data['Volume'].tolist()]
        }
        return JsonResponse(raw_data)

    except ValueError as ve:
        return JsonResponse({'error': f"Invalid input: {ve}"}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    

def simulation(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            body = json.loads(request.body)

            # Bind data to the form
            form = SimulationForm(body)
            
            # Validate the form
            if form.is_valid():
                # Access cleaned data
                data = form.cleaned_data
                symbol = data['symbol']
                start_date = data['start_date']
                end_date = data['end_date']
                initial_capital = data['initial_capital']
                fee = data['fee']
                risk = data['risk']
                strategy = data['strategy']

                # Perform simulation logic here (e.g., run the strategy, store results)
                return JsonResponse({'message': 'Simulation processed successfully', 'data': data})

            else:
                # Return form errors
                return JsonResponse({'error': 'Invalid input', 'details': form.errors}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
