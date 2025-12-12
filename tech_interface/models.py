# tech_interface/models.py
from django.db import models
from django.utils import timezone
from client.models import Espace, Profile


class Incident(models.Model):
    SEVERITE_CHOICES = [
        ('mineur', 'Mineur'),
        ('moyen', 'Moyen'),
        ('critique', 'Critique'),
        ('urgent', 'Urgent'),
    ]
    
    ETAT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('annule', 'Annulé'),
    ]
    
    espace = models.ForeignKey(Espace, on_delete=models.CASCADE, related_name='incidents')
    description = models.TextField()
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='moyen')
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='ouvert')
    technicien = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents_assignes')
    date_signalement = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Incident #{self.id} - {self.espace.nom}"
    
    @property
    def duree_resolution(self):
        if self.date_resolution and self.date_signalement:
            delta = self.date_resolution - self.date_signalement
            heures = delta.total_seconds() / 3600
            return round(heures, 1)
        return None


class Intervention(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('suspendue', 'Suspendue'),
    ]
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='interventions')
    espace = models.ForeignKey(Espace, on_delete=models.CASCADE)
    technicien = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='interventions')
    
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    
    # Notes détaillées
    note_debut = models.TextField(blank=True, help_text="État initial constaté")
    note_intervention = models.TextField(blank=True, help_text="Actions effectuées")
    note_fin = models.TextField(blank=True, help_text="Résultat et recommandations")
    
    # Photos
    photo_avant = models.ImageField(upload_to='interventions/avant/', null=True, blank=True)
    photo_apres = models.ImageField(upload_to='interventions/apres/', null=True, blank=True)
    
    # Matériel utilisé
    materiel_utilise = models.TextField(blank=True, help_text="Liste du matériel utilisé")
    cout_materiel = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Coût du matériel en €")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"Intervention #{self.id} - {self.technicien.user.get_full_name()}"
    
    @property
    def duree(self):
        if self.date_fin and self.date_debut:
            delta = self.date_fin - self.date_debut
            heures = delta.total_seconds() / 3600
            return round(heures, 1)
        elif self.date_debut:
            delta = timezone.now() - self.date_debut
            heures = delta.total_seconds() / 3600
            return round(heures, 1)
        return 0


class NoteIntervention(models.Model):
    """Notes ajoutées pendant l'intervention"""
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='notes')
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Note du {self.created_at.strftime('%d/%m/%Y %H:%M')}"