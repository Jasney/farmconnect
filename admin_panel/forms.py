from django import forms
from .models import UserReport


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ['report_type', 'title', 'description', 'evidence_attachment']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'evidence_attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
