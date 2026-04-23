from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["city", "date", "temp_max", "temp_min", "precipitation"]
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'temp_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temp_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'precipitation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
        }
