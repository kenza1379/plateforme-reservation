from django import forms
from client.models import Espace, Reservation, Profile
from django.contrib.auth.models import User


class EspaceForm(forms.ModelForm):
    class Meta:
        model = Espace
        fields = [
            'nom', 'description', 'type_espace', 'capacite', 
            'ville', 'adresse', 'equipements', 'prix_par_heure', 
            'image', 'disponible'
        ]


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['user', 'espace', 'date', 'heure_debut', 'duree_heures', 'prix_total', 'status', 'notes_admin']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'espace': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duree_heures': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'prix_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes_admin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_staff=False)
        self.fields['espace'].queryset = Espace.objects.filter(disponible=True)
        self.fields['prix_total'].required = False


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone',
            'address',
            'postal_code',
            'city',
            'gender',
            'nationality',
            'public_name',
            'birth_date',
            'default_card',
        ]