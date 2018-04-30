from django import forms
from .models import MediaPlan

class PlanForm(forms.ModelForm):
    class Meta:
        model = MediaPlan
        fields = ['name', 'budget', 'startDate', 'endDate', 'designer', 'client', 'audience', 'starter']
        labels = {
            "startDate": "From",
            "endDate": "To",
        }