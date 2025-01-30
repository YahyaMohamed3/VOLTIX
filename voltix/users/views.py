from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login , authenticate
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json

# Create your views here.
def landing_page(request):
    return render(request , "users/landing_page.html")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request , user)
            return redirect(reverse('trading:dashboard'))
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request , "users/register.html" , {'form':form})

def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return JsonResponse({'redirect_url': reverse('trading:dashboard')})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return render(request , "users/login.html")

def check_email(request):
   if request.method == "POST":
       data = json.loads(request.body)
       email = data.get('email' , '')
       exists = CustomUser.objects.filter(email=email).exists()
       return JsonResponse({'exists':exists})
   return JsonResponse({'exists':False}, status=400)


    
