from django.contrib import admin
from django.urls import path, include
import users 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("users.urls")),
    path('trading/', include('trading.urls')),
]
