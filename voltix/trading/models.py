from django.db import models
from django.contrib.auth import get_user_model

class PopularAssets(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    category = models.CharField(max_length=10 , choices=[('stock' , 'Stock') , ('crypto' , 'Crypto') , ('etf', 'ETF')])
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.name} ({self.ticker} ) - {self.category}"
    
    

User = get_user_model()

class Simulation(models.Model):
    SIMULATION_TYPES = [
        ('historical', 'Historical'),
        ('live', 'Live')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    simulation_type = models.CharField(max_length=20, choices=SIMULATION_TYPES)
    strategy_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    historical_period = models.CharField(max_length=100)
    
    # Initial Parameters
    initial_capital = models.FloatField()
    risk_level = models.FloatField()
    fee_percentage = models.FloatField()
    
    # Core Metrics
    total_return = models.FloatField()
    annualized_return = models.FloatField()
    win_rate = models.FloatField()
    
    def __str__(self):
        return f"{self.user.email} - {self.strategy_name} - {self.simulation_type}"

class StrategyMetrics(models.Model):
    simulation = models.OneToOneField(Simulation, on_delete=models.CASCADE, related_name='metrics')
    
    # Returns Analysis
    sharpe_ratio = models.FloatField()
    sortino_ratio = models.FloatField()
    best_month = models.FloatField()
    worst_month = models.FloatField()
    annualized_volatility = models.FloatField()
    
    # Risk Analysis
    max_drawdown = models.FloatField()
    avg_drawdown = models.FloatField()
    ulcer_index = models.FloatField()
    var_95 = models.FloatField(verbose_name="95% Value at Risk")
    cvar_95 = models.FloatField(verbose_name="95% Conditional VaR")
    
    # Trade Analysis
    profit_factor = models.FloatField()
    expectancy = models.FloatField()
    avg_win = models.FloatField()
    avg_loss = models.FloatField()
    max_win = models.FloatField()
    max_loss = models.FloatField()
    risk_reward_ratio = models.FloatField()
    
    # Time Analysis
    avg_holding_days = models.FloatField()
    median_holding_days = models.FloatField()
    max_holding_days = models.IntegerField()
    trades_per_year = models.FloatField()
    
    # Money Management
    kelly_criterion = models.FloatField()
    optimal_f = models.FloatField()
    max_consecutive_losses = models.IntegerField()
    avg_position_size = models.FloatField()
    
    # Simulations
    monte_carlo_positive = models.FloatField(verbose_name="MC Positive Outcomes %")
    best_simulation = models.FloatField()
    worst_simulation = models.FloatField()

    def __str__(self):
        return f"Metrics for {self.simulation}"


    


