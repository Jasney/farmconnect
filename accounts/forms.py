from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column
from .models import CustomUser, VerificationDocument, FarmerProfile

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': '+254 (7xx) xxx-xxx', 'class': 'form-control'}))
    location = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Your location', 'class': 'form-control'}))
    role = forms.ChoiceField(
        choices=[('farmer', 'Farmer'), ('buyer', 'Buyer')],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'role', 'password1', 'password2', 'phone', 'location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply form-control class to all fields except role
        for field_name, field in self.fields.items():
            if field_name not in ['role', 'password1', 'password2']:
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()


class FarmerProfileForm(forms.ModelForm):
    farm_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of your farm'
        })
    )
    farm_size_acres = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Farm size in acres',
            'step': '0.1'
        })
    )
    years_in_business = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Years in agriculture'
        })
    )
    
    class Meta:
        model = FarmerProfile
        fields = ['farm_name', 'farm_size_acres', 'years_in_business', 'farm_image']
        widgets = {
            'farm_image': forms.FileInput(attrs={'class': 'form-control'})
        }


class VerificationDocumentForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'document_type': 'Document Type',
            'document_file': 'Upload Document (PDF, JPG, PNG)',
        }


class FarmerVerificationForm(forms.ModelForm):
    """Form for farmers to submit verification details"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'national_id', 'phone', 'location', 'profile_image', 'kyc_document']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID Number'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'kyc_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'national_id': 'National ID Number',
            'kyc_document': 'Identification Document (PDF, JPG, PNG)',
            'profile_image': 'Profile Photo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit for Verification', css_class='btn btn-primary'))


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_classes + ' form-control').strip()
            field.widget.attrs['aria-invalid'] = 'false'
            field.widget.attrs['aria-describedby'] = f'{field_name}_errors'
        
        # Update aria-invalid to 'true' for fields with errors
        for field_name in self.errors:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['aria-invalid'] = 'true'
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
            Submit('submit', 'Login', css_class='btn btn-success btn-lg w-100'),
        )

class AppealForm(forms.Form):
    issue_summary = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of your appeal'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Explain why your account should be unblocked'}))


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

