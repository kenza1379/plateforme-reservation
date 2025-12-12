from django.contrib import admin
from .models import Espace, EspaceImage, Reservation, Profile, PaymentCard, ActiveSession

# Espace avec configuration personnalisée
@admin.register(Espace)
class EspaceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_espace', 'capacite', 'ville', 'prix_par_heure', 'disponible')
    list_filter = ('type_espace', 'ville', 'disponible')
    search_fields = ('nom', 'ville', 'type_espace')

# Les autres modèles avec enregistrement classique
admin.site.register(EspaceImage)
admin.site.register(Reservation)
admin.site.register(Profile)
admin.site.register(PaymentCard)
admin.site.register(ActiveSession)
