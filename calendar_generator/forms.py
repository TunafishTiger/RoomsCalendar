import datetime

from django import forms

from .models import CalendarGeneration


class CalendarGenerationForm(forms.ModelForm):
    """Form for generating a calendar."""

    class Meta:
        model = CalendarGeneration
        fields = ['room_type', 'month', 'year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default month to next month
        today = datetime.date.today()
        next_month = today.month + 1 if today.month < 12 else 1
        next_month_year = today.year if today.month < 12 else today.year + 1

        self.fields['month'].initial = next_month
        self.fields['year'].initial = next_month_year

        # Add custom labels and help text
        self.fields['room_type'].label = "Room Type"
        self.fields['month'].label = "Month"
        self.fields['year'].label = "Year"

        # Add custom widgets
        self.fields['room_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['month'].widget.attrs.update({'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
