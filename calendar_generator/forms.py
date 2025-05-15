import datetime

from django import forms

from .models import CalendarGeneration


class CalendarGenerationForm(forms.ModelForm):
    """Form for generating a calendar."""

    class Meta:
        model = CalendarGeneration
        fields = ['room_type', 'month']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default month to next month
        today = datetime.date.today()
        next_month = today.month + 1 if today.month < 12 else 1

        self.fields['month'].initial = next_month

        # Add custom labels and help text
        self.fields['room_type'].label = "Room Type"
        self.fields['month'].label = "Month"

        # Add custom widgets
        self.fields['room_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['month'].widget.attrs.update({'class': 'form-control'})
