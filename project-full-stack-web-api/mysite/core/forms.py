from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["city", "date", "temp_max", "temp_min", "precipitation"]
