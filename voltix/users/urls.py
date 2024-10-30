from django.urls import path 
from . import views 

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("register" , views.register , name="register"),
    path("login" , views.login, name="login"),
    #api
    path("check_email/" , views.check_email, name="check_email"),
]