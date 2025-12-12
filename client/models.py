from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date, time


class Espace(models.Model):
    TYPE_CHOICES = [
        ('petite_salle', 'Petite salle'),
        ('moyenne_salle', 'Moyenne salle'),
        ('grande_salle', 'Grande salle'),
        ('reunion', 'Salle de réunion'),
        ('brainstorming', 'Salle de brainstorming'),
        ('studio', 'Salle de studio'),
        ('espace_detente', 'Espace détente'),
        ('espace_formation', 'Salle de formation'),
    ]

    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type_espace = models.CharField(max_length=50, choices=TYPE_CHOICES)
    capacite = models.PositiveIntegerField()
    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200, blank=True)
    equipements = models.TextField(blank=True)
    prix_par_heure = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='espaces/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.ville})"


class EspaceImage(models.Model):
    espace = models.ForeignKey(Espace, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='espaces/')

    def __str__(self):
        return f"Image de {self.espace.nom}"


class PaymentCard(models.Model):
    CARD_TYPES = [
        ('Visa', 'Visa'),
        ('Mastercard', 'Mastercard'),
        ('AMEX', 'AMEX'),
        ('Discover', 'Discover'),
        ('JCB', 'JCB'),
        ('Diners', 'Diners'),
        ('UnionPay', 'UnionPay'),
        ('CB', 'CB'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_cards")
    name = models.CharField(max_length=100)
    last_four = models.CharField(max_length=4)
    type = models.CharField(max_length=20, choices=CARD_TYPES)
    expiry = models.CharField(max_length=5)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} •••• {self.last_four} ({self.user.username})"


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('O', 'Autre'),
    ]

    ROLE_CHOICES = [
        ('client', 'Client'),
        ('technicien', 'Technicien'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    public_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    default_card = models.ForeignKey('PaymentCard', on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.user.username} - Profile ({self.role})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class ActiveSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    device_info = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.device_info}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    espace = models.ForeignKey("Espace", on_delete=models.CASCADE, related_name="reservations")
    date = models.DateField(default=date.today)
    heure_debut = models.TimeField(default=time(9, 0))
    duree_heures = models.PositiveIntegerField(default=1)
    prix_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, verbose_name="Payé")
    payment_method = models.CharField(max_length=100, blank=True, verbose_name="Méthode de paiement")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    notes_admin = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("espace", "date", "heure_debut")
        ordering = ['-date', 'heure_debut']

    def __str__(self):
        return f"{self.user.username} - {self.espace.nom} le {self.date} à {self.heure_debut}"
    
    @property
    def heure_fin(self):
        from datetime import datetime, timedelta
        debut = datetime.combine(self.date, self.heure_debut)
        fin = debut + timedelta(hours=self.duree_heures)
        return fin.time()
    
    @property
    def date_fin(self):
        from datetime import datetime, timedelta
        debut = datetime.combine(self.date, self.heure_debut)
        fin = debut + timedelta(hours=self.duree_heures)
        return fin.date()
    

class Favori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    espace = models.ForeignKey(Espace, on_delete=models.CASCADE, related_name='favoris')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'espace')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.espace.nom}"