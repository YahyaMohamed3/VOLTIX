from django.contrib import admin
from .models import PopularAssets

# Register the PopularAssets model in the Django admin panel
@admin.register(PopularAssets)
class PopularAssetsAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'category', 'logo_url', 'created_at')
    search_fields = ['name', 'ticker']
    list_filter = ['category']
