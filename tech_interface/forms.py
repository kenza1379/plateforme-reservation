from django import forms
from .models import Incident, Intervention, Salle, Reservation

# ------------------------
# Formulaire Incident
# ------------------------
class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'salle',
            'description',
            'severite',
            'technicien',
            'estimation_remise_en_service',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'estimation_remise_en_service': forms.TimeInput(attrs={'type': 'time'}),
        }

# ------------------------
# Formulaire Intervention
# ------------------------
class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'incident',
            'salle',
            'technicien',
            'date_debut',
            'date_fin',
            'statut',
            'notes',
        ]
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# ------------------------
# Formulaire Salle
# ------------------------
class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = [
            'nom',
            'capacite',
            'disponible',
            'maintenance_until',
        ]
        widgets = {
            'maintenance_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# ------------------------
# Formulaire Reservation
# ------------------------
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'salle',
            'client',
            'date_debut',
            'date_fin',
            'status',
        ]
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
