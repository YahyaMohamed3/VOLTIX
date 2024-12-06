from django.db import models

class popluar_assets(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    category = models.CharField(max_length=10 , choices=[('stock' , 'Stock') , ('crypto' , 'Crypto') , ('etf', 'ETF')])
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.name} ({self.ticker} ) - {self.category}"
    
