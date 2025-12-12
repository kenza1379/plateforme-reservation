from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone


from .models import Incident, Intervention
from client.models import Espace, Profile


@login_required
def dashboard(request):
    espaces = Espace.objects.all()
    en_maintenance_count = espaces.filter(disponible=False).count()
    incidents_ouverts = Incident.objects.exclude(etat__in=['resolu', 'annule']).count()

    context = {
        'total_salles': espaces.count(),
        'en_maintenance': en_maintenance_count,
        'incidents_ouverts': incidents_ouverts,
    }
    return render(request, 'tech_interface/dashboard.html', context)


@login_required
def salles_status(request):
    espaces = Espace.objects.all().order_by('nom')
    return render(request, 'tech_interface/salles_status.html', {'salles': espaces})


@login_required
def incident_list(request):
    # Tous les incident
    incidents = Incident.objects.all().order_by('-date_signalement')
    return render(request, 'tech_interface/incidents.html', {'incidents': incidents})


@login_required
def incident_create(request):
    if request.method == 'POST':
        espace_id = request.POST.get('espace')
        description = request.POST.get('description')
        severite = request.POST.get('severite', 'mineur')
        
        espace = get_object_or_404(Espace, id=espace_id)
        
        Incident.objects.create(
            espace=espace,
            description=description,
            severite=severite,
            etat='ouvert',
            date_signalement=timezone.now()
        )
        return redirect('tech_interface:incidents_list')
    
    espaces = Espace.objects.all()
    return render(request, 'tech_interface/form_incident.html', {'espaces': espaces})


@login_required
def incident_start(request, id):
    incident = get_object_or_404(Incident, id=id)
    incident.etat = 'en_cours'

    # Assigner le technicien connecté si c'est un technicien
    try:
        technicien_profile = request.user.profile
        if technicien_profile.role == 'technicien':
            incident.technicien = technicien_profile
    except:
        pass
    
    incident.save()

    Intervention.objects.create(
        incident=incident,
        espace=incident.espace,
        technicien=incident.technicien,
        date_debut=timezone.now(),
        statut='en_cours',
    )

    incident.espace.disponible = False
    incident.espace.save()

    intervention = Intervention.objects.filter(incident=incident, statut='en_cours').first()
    return redirect('tech_interface:intervention_detail', intervention_id=intervention.id)


@login_required
def incident_finish(request, id):
    incident = get_object_or_404(Incident, id=id)
    incident.etat = 'resolu'
    incident.save()

    intervention = incident.interventions.filter(statut='en_cours').first()
    if intervention:
        intervention.statut = 'terminee'
        intervention.date_fin = timezone.now()
        intervention.save()

    incident.espace.disponible = True
    incident.espace.save()

    return redirect('tech_interface:incidents_list')


@login_required
def salle_set_maintenance(request, id):
    espace = get_object_or_404(Espace, id=id)
    espace.disponible = False
    espace.save()
    return redirect('tech_interface:salles_status')


@login_required
def salle_reactivate(request, id):
    espace = get_object_or_404(Espace, id=id)
    espace.disponible = True
    espace.save()
    return redirect('tech_interface:salles_status')


@login_required
def intervention_detail(request, intervention_id):
    intervention = get_object_or_404(Intervention, id=intervention_id)
    return render(request, 'tech_interface/intervention_detail.html', {'intervention': intervention})
