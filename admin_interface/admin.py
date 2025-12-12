from django.contrib import admin
from tech_interface.models import Incident, Intervention
from client.models import Profile, Espace

# Enregistrer les modèles pour l'interface admin Django
admin.site.register(Incident)
admin.site.register(Intervention)