from django.urls import path 
from . import views 

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("register" , views.register , name="register"),
    #api
    path("login/" , views.login, name="login"),
    path("check_email/" , views.check_email, name="check_email"),
]