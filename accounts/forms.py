from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from accounts.models import Reservation

class ExportExcelForm(forms.Form):
    from_date = JalaliDateField(
        label="از تاریخ",
        required=False,
        widget=AdminJalaliDateWidget,
    )

    to_date = JalaliDateField(
        label="تا تاریخ",
        required=False,
        widget=AdminJalaliDateWidget,
    )

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = "__all__"