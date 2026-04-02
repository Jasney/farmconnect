from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column
from .models import Crop, PurchaseRequest, Review

class CropForm(forms.ModelForm):
    UNIT_CHOICES = (
        ('kg', 'Kilograms (kg)'),
        ('bags', 'Bags'),
        ('tons', 'Tons'),
        ('pieces', 'Pieces'),
        ('liters', 'Liters'),
        ('other', 'Other'),
    )
    
    unit = forms.ChoiceField(choices=UNIT_CHOICES, initial='kg')
    
    class Meta:
        model = Crop
        fields = ['name', 'type', 'price_per_unit', 'quantity_available', 'unit', 'description', 'image', 'is_organic', 'quality_grade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('type', css_class='col-md-6'),
            ),
            Row(
                Column('price_per_unit', css_class='col-md-4'),
                Column('quantity_available', css_class='col-md-4'),
                Column('unit', css_class='col-md-4'),
            ),
            Row(
                Column('quality_grade', css_class='col-md-6'),
                Column('is_organic', css_class='col-md-6'),
            ),
            'description',
            'image',
            Submit('submit', 'Create Listing', css_class='btn btn-success btn-lg w-100 mt-3'),
        )
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].choices = [('', 'Select Category')] + list(self.fields['type'].choices)


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['quantity_requested', 'message']
        widgets = {
            'quantity_requested': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Add any special requests or questions'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES, attrs={'class': 'form-check-input'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your review a title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your experience with this product and farmer'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity_requested'].widget.attrs.update({'class': 'form-control', 'min': 1})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'rows': 4, 'placeholder': 'Optional message to the farmer'})
