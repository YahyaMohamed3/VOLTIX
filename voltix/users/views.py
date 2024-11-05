from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login 
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.http import JsonResponse
import json

# Create your views here.
def landing_page(request):
    return render(request , "users/landing_page.html")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request)
            return redirect('landing_page')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request , "users/register.html" , {'form':form})

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('landing_page')
    else:
        return render(request , "users/login.html")

def check_email(request):
   if request.method == "POST":
       data = json.loads(request.body)
       email = data.get('email' , '')
       exists = CustomUser.objects.filter(email=email).exists()
       return JsonResponse({'exists':exists})
   return JsonResponse({'exists':False}, status=400)


    
