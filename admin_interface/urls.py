from django.urls import path
from . import views
from client.models import Espace

app_name = "admin_interface"   # Obligatoire pour utiliser {% url 'admin_interface:...' %}

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # --------------------------
    # Gestion des salles
    # --------------------------
    path('espaces/', views.espace_list, name='espace_list'),
    path('espaces/ajouter/', views.espace_create, name='espace_create'),
    path('espaces/<int:id>/modifier/', views.espace_update, name='espace_update'),
    path('espaces/<int:id>/supprimer/', views.espace_delete, name='espace_delete'),

    # --------------------------
    # Gestion des réservations
    # --------------------------

    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/ajouter/', views.reservation_create, name='reservation_create'),

    path('reservations/modifier/<int:id>/', views.reservation_update, name='reservation_update'),
    path('reservations/valider/<int:id>/', views.reservation_valider, name='reservation_valider'),
    
    path('reservations/refuser/<int:id>/', views.reservation_refuser, name='reservation_refuser'),
    path('reservations/supprimer/<int:id>/', views.reservation_delete, name='reservation_delete'),

    # --------------------------
    # Gestion des techniciens (A faire)
    # --------------------------
    path('techniciens/', views.technicien_list, name='technicien_list'),
    path('techniciens/ajouter/', views.technicien_create, name='technicien_create'),
    path('techniciens/modifier/<int:id>/', views.technicien_update, name='technicien_update'),
    path('techniciens/supprimer/<int:id>/', views.technicien_delete, name='technicien_delete'),

    # --------------------------
    # Statistiques
    # --------------------------
    path('statistiques/', views.statistiques, name='statistiques'),

    # --------------------------
    # Gestion des clients
    # --------------------------
    path('clients/', views.client_list, name='client_list'),
    path('clients/ajouter/', views.client_create, name='client_create'),
    path('clients/modifier/<int:id>/', views.client_update, name='client_update'),
    path('clients/supprimer/<int:id>/', views.client_delete, name='client_delete'),


    path('forbidden/', views.forbidden, name='forbidden'),
    path('logout/', views.logout_admin, name='logout_admin'),


    # Interventions - Suivi
    path('interventions/', views.interventions_suivi, name='interventions_suivi'),
    path('intervention/create/', views.intervention_create, name='intervention_create'),
    path('intervention/update/', views.intervention_update, name='intervention_update'),
    path('intervention/<int:intervention_id>/close/', views.intervention_close, name='intervention_close'),
    path('intervention/<int:intervention_id>/details/', views.intervention_details_api, name='intervention_details'),
    path('intervention/<int:intervention_id>/data/', views.intervention_data_api, name='intervention_data'),
    
    # Performance technicien
    path('technicien/<int:technicien_id>/performance/', views.technicien_performance, name='technicien_performance'),

]
