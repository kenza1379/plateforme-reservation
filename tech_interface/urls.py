from django.urls import path
from . import views

app_name = 'tech_interface'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # État des salles
    path('salles/', views.salles_status, name='salles_status'),

    # Incidents
    path('incidents/', views.incident_list, name='incidents_list'),
    path('incidents/new/', views.incident_create, name='incident_create'),
    path('incidents/start/<int:id>/', views.incident_start, name='incident_start'),
    path('incidents/finish/<int:id>/', views.incident_finish, name='incident_finish'),

    # Maintenance des salles
    path('salles/maintenance/<int:id>/', views.salle_set_maintenance, name='salle_set_maintenance'),
    path('salles/reactiver/<int:id>/', views.salle_reactivate, name='salle_reactivate'),

    path('intervention/<int:intervention_id>/', views.intervention_detail, name='intervention_detail'),
]
