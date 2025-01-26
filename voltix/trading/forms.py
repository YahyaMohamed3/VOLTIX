from django import forms 


class SimulationForm(forms.Form):
    symbol = forms.CharField(max_length=10, required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    initial_capital = forms.DecimalField(max_digits=20, decimal_places=2, required=True)
    fee = forms.DecimalField(max_digits=10, decimal_places=5, required=True)
    risk = forms.CharField(max_length=10, required=True)  # Change to CharField
    strategy = forms.CharField(max_length=50, required=True)