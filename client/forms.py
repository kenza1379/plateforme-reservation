from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'heure_debut', 'duree_heures']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat()  
            }),
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'duree_heures': forms.Select(
                attrs={'class': 'form-select'},
                choices=[(1, '1h'), (2, '2h'), (3, '3h'), (4, '4h')]
            )
        }

    def __init__(self, *args, **kwargs):
        self.espace = kwargs.pop('espace', None)
        super().__init__(*args, **kwargs)

    def clean_date(self):
        """Valider que la date n'est pas dans le passé"""
        selected_date = self.cleaned_data.get('date')
        
        if selected_date and selected_date < date.today():
            raise ValidationError("Vous ne pouvez pas réserver une date dans le passé.")
        
        return selected_date

    def clean(self):
        """Validation globale : date + heure + conflits"""
        cleaned_data = super().clean()
        selected_date = cleaned_data.get('date')
        selected_time = cleaned_data.get('heure_debut')


        if selected_date and selected_time:
            selected_datetime = datetime.combine(selected_date, selected_time)
            now = datetime.now()
            
            if selected_datetime < now:
                raise ValidationError("Vous ne pouvez pas réserver dans le passé.")


        if self.espace and selected_date and selected_time:
            exists = Reservation.objects.filter(
                espace=self.espace,
                date=selected_date,
                heure_debut=selected_time
            ).exists()
            
            if exists:
                raise ValidationError("Ce créneau est déjà réservé.")
        
        return cleaned_data

    def save(self, commit=True, user=None):
        reservation = super().save(commit=False)
        if self.espace:
            reservation.espace = self.espace
            reservation.prix_total = self.espace.prix_par_heure * reservation.duree_heures
        if user:
            reservation.user = user
        if commit:
            reservation.save()
        return reservation