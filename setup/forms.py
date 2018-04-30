from django import forms
from .models import TargetGroup, Publication, Client

class GroupForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(Publication.objects, required=False)

    class Meta:
        model = TargetGroup
        fields = ('__all__')

class PublicationForm(forms.ModelForm):
    contactName = forms.CharField(required=False, label="Contact Name")
    class Meta: 
        model = Publication
        fields = ('__all__')
        labels = {
            "contactName": "Contact Name",
            "email": "Email Address",
            "phone": "Phone Number",
            "targetGroups": "Target Groups",
        }

class ClientForm(forms.ModelForm):
    contactName = forms.CharField(required=False, label="Contact Name")
    class Meta:
        model = Client
        fields = ('__all__')
        labels = {
            "contactName": "Contact Name",
            "email": "Email Address",
            "phone": "Phone Number",
        }