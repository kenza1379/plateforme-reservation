from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib import messages

from client.models import Profile, Espace, Reservation
from .forms import EspaceForm, ReservationForm, UserForm, ProfileForm
from django.http import JsonResponse
from django.db.models import Avg, Count, Sum
from datetime import timedelta
from tech_interface.models import Intervention, Incident
from django.utils import timezone


# Vérifie si l'utilisateur est admin
def is_admin(user):
    return user.is_authenticated and user.is_staff


# --------------------
# TABLEAU DE BORD ADMIN
# --------------------
@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def dashboard(request):
    total_espaces = Espace.objects.count()
    total_clients = User.objects.filter(is_staff=False).count()
    total_reservations = Reservation.objects.count()
    total_techniciens = Profile.objects.filter(role='technicien').count()

    return render(request, 'admin_interface/dashboard.html', {
        'total_espaces': total_espaces,
        'total_clients': total_clients,
        'total_reservations': total_reservations,
        'total_techniciens': total_techniciens,
    })


# --------------------
# GESTION DES ESPACES
# --------------------

@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def espace_list(request):
    espaces = Espace.objects.all()
    return render(request, 'admin_interface/espaces.html', {'espaces': espaces})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def espace_create(request):
    form = EspaceForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('admin_interface:espace_list')
    return render(request, 'admin_interface/form_espace.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def espace_update(request, id):
    espace = get_object_or_404(Espace, id=id)
    form = EspaceForm(request.POST or None, request.FILES or None, instance=espace)
    if form.is_valid():
        form.save()
        return redirect('admin_interface:espace_list')
    return render(request, 'admin_interface/form_espace.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def espace_delete(request, id):
    espace = get_object_or_404(Espace, id=id)
    espace.delete()
    return redirect('admin_interface:espace_list')


# --------------------
# GESTION DES CLIENTS (USER + PROFILE)
# --------------------

@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def client_list(request):
    clients = User.objects.filter(is_staff=False)
    return render(request, 'admin_interface/client_list.html', {'clients': clients})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def client_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            
            mot_de_passe_defaut = user.last_name
            user.set_password(mot_de_passe_defaut)
            user.save()

            profile = user.profile
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            profile_form.save()

            messages.success(
                request, 
                f"Client créé avec succès ! Mot de passe par défaut : <strong>{mot_de_passe_defaut}</strong>"
            )
            
            return redirect('admin_interface:client_list')
    else:
        form = UserForm()
        profile_form = ProfileForm()

    return render(request, 'admin_interface/form_client.html', {
        'form': form,
        'profile_form': profile_form
    })


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def client_update(request, id):  
    user = get_object_or_404(User, id=id)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "Client mis à jour avec succès !")
            return redirect('admin_interface:client_list')
    else:
        form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'admin_interface/form_client.html', {
        'form': form,
        'profile_form': profile_form
    })


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def client_delete(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('admin_interface:client_list')


# --------------------
# GESTION DES RÉSERVATIONS
# --------------------

@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_list(request):
    reservations = Reservation.objects.select_related('user', 'espace').all()
    return render(request, 'admin_interface/reservations.html', {'reservations': reservations})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_valider(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    reservation.status = "validee"  
    reservation.save()
    messages.success(request, "Réservation validée avec succès !")
    return redirect('admin_interface:reservation_list')


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_refuser(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    reservation.status = "refusee"  
    reservation.save()
    return redirect('admin_interface:reservation_list')


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_create(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            
            # Calculer automatiquement le prix total
            if reservation.espace and reservation.duree_heures:
                reservation.prix_total = reservation.espace.prix_par_heure * reservation.duree_heures
            
            reservation.save()
            messages.success(request, "Réservation créée avec succès.")
            return redirect('admin_interface:reservation_list')
    else:
        form = ReservationForm()
    
    # Passer les espaces avec leur prix au template
    espaces = Espace.objects.filter(disponible=True).values('id', 'nom', 'prix_par_heure')
    
    return render(request, 'admin_interface/form_reservation.html', {
        'form': form,
        'espaces': espaces,
    })


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_update(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Réservation mise à jour.")
            return redirect('admin_interface:reservation_list')
    else:
        form = ReservationForm(instance=reservation)
    
    # Passer les espaces avec leur prix au template
    espaces = Espace.objects.filter(disponible=True).values('id', 'nom', 'prix_par_heure')

    return render(request, 'admin_interface/form_reservation.html', {
        'form': form,
        'reservation': reservation,
        'espaces': espaces,
    })


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def reservation_delete(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    reservation.delete()
    messages.success(request, 'Réservation supprimée avec succès !')
    return redirect('admin_interface:reservation_list')


# --------------------
# GESTION DES TECHNICIENS
# --------------------

@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def technicien_list(request):
    """
    Affiche la liste des techniciens (Profiles avec role='technicien')
    """
    techniciens = Profile.objects.filter(role='technicien').select_related('user')
    return render(request, 'admin_interface/techniciens.html', {'techniciens': techniciens})


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def technicien_create(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        
        # Validation basique
        if not all([nom, prenom, email]):
            messages.error(request, "Nom, prénom et email sont obligatoires")
            return render(request, 'admin_interface/form_technicien.html')
        
        # Vérifier si l'email existe déjà
        if User.objects.filter(email=email).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà")
            return render(request, 'admin_interface/form_technicien.html')
        
        # Générer un username unique basé sur l'email
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Mot de passe par défaut = nom
        mot_de_passe = nom
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=mot_de_passe,
            first_name=prenom,
            last_name=nom,
            is_staff=False
        )
        
        profile = user.profile
        profile.role = 'technicien'
        profile.phone = telephone
        profile.save()

        messages.success(
            request,
            f"Technicien créé ! Identifiant : <strong>{username}</strong> | Mot de passe : <strong>{mot_de_passe}</strong>"
        )
        return redirect('admin_interface:technicien_list')
    
    return render(request, 'admin_interface/form_technicien.html')


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def technicien_update(request, id):
    """
    Modification d'un technicien (Profile)
    """
    profile = get_object_or_404(Profile, id=id, role='technicien')
    user = profile.user
    
    if request.method == "POST":
        # Récupérer les données
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        
        # Validation
        if not all([nom, prenom, email]):
            messages.error(request, "Nom, prénom et email sont obligatoires")
            return render(request, 'admin_interface/form_technicien.html', {
                'profile': profile,
                'editing': True
            })
        
        # Vérifier si l'email est déjà utilisé par un autre user
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Cet email est déjà utilisé")
            return render(request, 'admin_interface/form_technicien.html', {
                'profile': profile,
                'editing': True
            })
        
        # Mettre à jour l'utilisateur
        user.first_name = prenom
        user.last_name = nom
        user.email = email
        user.save()
        
        # Mettre à jour le profil
        profile.phone = telephone
        profile.save()
        
        messages.success(request, "Technicien mis à jour avec succès")
        return redirect('admin_interface:technicien_list')
    
    return render(request, 'admin_interface/form_technicien.html', {
        'profile': profile,
        'editing': True
    })


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def technicien_delete(request, id):
    """
    Suppression d'un technicien (Profile + User)
    """
    profile = get_object_or_404(Profile, id=id, role='technicien')
    user = profile.user
    
    user.delete()
    
    messages.success(request, "Technicien supprimé avec succès")
    return redirect('admin_interface:technicien_list')


# --------------------
# STATISTIQUES
# --------------------

@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def statistiques(request):
    stats = {
        'nb_salles': Espace.objects.count(),
        'nb_reservations': Reservation.objects.count(),
        'nb_techniciens': Profile.objects.filter(role='technicien').count(),
        'nb_clients': User.objects.filter(is_staff=False).count()
    }
    return render(request, 'admin_interface/statistiques.html', stats)


# --------------------
# LOGOUT ADMIN
# --------------------

def forbidden(request):
    return HttpResponseForbidden("Accès refusé : vous n'avez pas les droits administrateur.")


def logout_admin(request):
    logout(request)
    return redirect('login')


# --------------------
# SUIVI DES INTERVENTIONS
# --------------------



@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def intervention_create(request):
    """Créer une nouvelle intervention"""
    if request.method == 'POST':
        try:
            salle_id = request.POST.get('salle')
            technicien_id = request.POST.get('technicien')
            description = request.POST.get('description')
            priorite = request.POST.get('priorite', 'moyenne')
            cout_estime = request.POST.get('cout_estime', 0)
            
            # Validation
            if not all([salle_id, technicien_id, description]):
                return JsonResponse({
                    'success': False,
                    'error': 'Tous les champs obligatoires doivent être remplis'
                }, status=400)
            
            # Objets
            espace = get_object_or_404(Espace, id=salle_id)
            technicien = get_object_or_404(Profile, id=technicien_id, role='technicien')
            
            severite_map = {
                'basse': 'mineur',
                'moyenne': 'moyen',
                'haute': 'critique',
                'urgente': 'urgent'
            }
            
            # Incident
            incident = Incident.objects.create(
                espace=espace,
                description=description,
                severite=severite_map.get(priorite, 'moyen'),
                date_signalement=timezone.now(),
                etat='ouvert'
            )
            
            # Intervention
            intervention = Intervention.objects.create(
                incident=incident,
                technicien=technicien,
                espace=espace,
                date_debut=timezone.now(),
                statut='en_cours',
                cout_materiel=float(cout_estime) if cout_estime else 0,
                note_debut=f"Incident créé par admin - Priorité: {priorite}"
            )

            # Mettre à jour état incident
            incident.etat = 'en_cours'
            incident.save()

            # Mettre la salle en maintenance
            espace.disponible = False
            espace.en_maintenance = True
            espace.maintenance_until = None
            espace.save()

            messages.success(
                request,
                f'Intervention #{intervention.id} créée avec succès'
            )

        except Exception as e:
            messages.error(request, f'Erreur lors de la création de l\'intervention')

        return redirect('admin_interface:interventions_suivi')

    return redirect('admin_interface:interventions_suivi')




@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def intervention_update(request):
    """Modifier une intervention existante"""
    if request.method == 'POST':
        try:
            intervention_id = request.POST.get('intervention_id')
            intervention = get_object_or_404(Intervention, id=intervention_id)
            
            # Récupérer les nouvelles données
            salle_id = request.POST.get('salle')
            technicien_id = request.POST.get('technicien')
            description = request.POST.get('description')
            priorite = request.POST.get('priorite')
            cout_estime = request.POST.get('cout_estime', 0)
            
            # Mise à jour
            if salle_id:
                intervention.espace = get_object_or_404(Espace, id=salle_id)
            
            if technicien_id:
                nouveau_technicien = get_object_or_404(Profile, id=technicien_id, role='technicien')
                if intervention.technicien.id != int(technicien_id):
                    intervention.technicien = nouveau_technicien
            
            if description and intervention.incident:
                intervention.incident.description = description
                intervention.incident.save()
            
            if priorite and intervention.incident:
                # Mapper priorite vers severite
                severite_map = {
                    'basse': 'mineur',
                    'moyenne': 'moyen',
                    'haute': 'critique',
                    'urgente': 'urgent'
                }
                intervention.incident.severite = severite_map.get(priorite, 'moyen')
                intervention.incident.save()
            
            if cout_estime:
                intervention.cout_materiel = float(cout_estime)
            
            intervention.save()
            
            messages.success(request, f'Intervention #{intervention.id} mise à jour avec succès')
            return redirect('admin_interface:interventions_suivi')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification de l\'intervention')
            return redirect('admin_interface:interventions_suivi')
    
    return redirect('admin_interface:interventions_suivi')


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def intervention_close(request, intervention_id):
    """Clôturer une intervention et réactiver l'espace"""
    if request.method == 'POST':
        try:
            intervention = get_object_or_404(Intervention, id=intervention_id)
            
            # Vérifier qu'elle n'est pas déjà terminée
            if intervention.statut == 'terminee':
                return JsonResponse({
                    'success': False,
                    'error': 'Cette intervention est déjà terminée'
                })
            
            # Calculer la durée si pas déjà définie
            if not intervention.duree and intervention.date_debut:
                duree_delta = timezone.now() - intervention.date_debut
                intervention.duree = round(duree_delta.total_seconds() / 3600, 2)
            
            # Clôturer l'intervention
            intervention.statut = 'terminee'
            intervention.date_fin = timezone.now()
            intervention.save()
            
            # Réactiver l'espace
            espace = intervention.espace
            espace.disponible = True
            espace.en_maintenance = False
            espace.maintenance_until = None
            espace.save()
            
            # Marquer l'incident comme résolu
            if intervention.incident:
                intervention.incident.etat = 'resolu'
                intervention.incident.date_resolution = timezone.now()
                intervention.incident.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Intervention #{intervention.id} clôturée avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)






@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def intervention_data_api(request, intervention_id):
    """API pour récupérer les données d'une intervention pour l'édition"""
    try:
        intervention = get_object_or_404(Intervention, id=intervention_id)
        
        # Mapper severite vers priorite pour l'affichage
        severite_to_priorite = {
            'mineur': 'basse',
            'moyen': 'moyenne',
            'critique': 'haute',
            'urgent': 'urgente'
        }
        
        data = {
            'id': intervention.id,
            'espace_id': intervention.espace.id,
            'technicien_id': intervention.technicien.id,
            'description': intervention.incident.description if intervention.incident else '',
            'priorite': severite_to_priorite.get(intervention.incident.severite, 'moyenne') if intervention.incident else 'moyenne',
            'cout_materiel': float(intervention.cout_materiel),
            'statut': intervention.statut,
        }
        
        return JsonResponse(data)
        
    except Intervention.DoesNotExist:
        return JsonResponse({'error': 'Intervention non trouvée'}, status=404)



@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def intervention_details_api(request, intervention_id):
    """API pour récupérer les détails d'une intervention"""
    try:
        intervention = Intervention.objects.select_related(
            'technicien__user', 'espace', 'incident'
        ).get(id=intervention_id)
        
        severite_to_priorite = {
        'mineur': '🟢 Basse',
        'moyen': '🟡 Moyenne',
        'critique': '🔴 Haute',
        'urgent': '🚨 Urgente'
        }

        data = {
            'id': intervention.id,
            'technicien': intervention.technicien.user.get_full_name(),
            'espace': intervention.espace.nom,
            'duree': intervention.duree or 'En cours',
            'cout': float(intervention.cout_materiel),
            'description': intervention.incident.description if intervention.incident else '',
            'priorite': severite_to_priorite.get(intervention.incident.severite, '🟡 Moyenne') if intervention.incident else '🟡 Moyenne',
            'note_debut': intervention.note_debut,
            'note_intervention': intervention.note_intervention,
            'materiel': intervention.materiel_utilise,
            'photo_avant': intervention.photo_avant.url if intervention.photo_avant else None,
            'photo_apres': intervention.photo_apres.url if intervention.photo_apres else None,
            'photos': bool(intervention.photo_avant or intervention.photo_apres),
        }
        
        return JsonResponse(data)
    except Intervention.DoesNotExist:
        return JsonResponse({'error': 'Intervention non trouvée'}, status=404)


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def technicien_performance(request, technicien_id):
    """Vue des performances d'un technicien spécifique"""
    technicien = get_object_or_404(Profile, id=technicien_id, role='technicien')
    
    interventions = Intervention.objects.filter(
        technicien=technicien
    ).select_related('espace', 'incident')
    
    # Stats du technicien
    total_interventions = interventions.count()
    interventions_terminees = interventions.filter(statut='terminee')
    
    if interventions_terminees.exists():
        temps_moyen = sum([i.duree for i in interventions_terminees if i.duree]) / interventions_terminees.count()
    else:
        temps_moyen = 0
    
    cout_total = interventions.aggregate(total=Sum('cout_materiel'))['total'] or 0
    
    context = {
        'technicien': technicien,
        'total_interventions': total_interventions,
        'interventions_terminees': interventions_terminees.count(),
        'interventions_en_cours': interventions.filter(statut='en_cours').count(),
        'temps_moyen': round(temps_moyen, 1),
        'cout_total': cout_total,
        'interventions': interventions.order_by('-date_debut')[:20],
    }
    
    return render(request, 'admin_interface/technicien_performance.html', context)


@login_required
@user_passes_test(is_admin, login_url='/forbidden/')
def interventions_suivi(request):
    """Vue principale du suivi des interventions pour l'admin"""
    
    # Filtrer par mois en cours
    from django.utils import timezone
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    
    # Récupérer toutes les interventions
    interventions = Intervention.objects.select_related(
        'technicien__user', 'espace', 'incident'
    ).order_by('-date_debut')
    
    # Statistiques
    interventions_terminees = interventions.filter(statut='terminee')
    
    # Calcul manuel du temps moyen en heures
    if interventions_terminees.exists():
        total_heures = sum([i.duree for i in interventions_terminees if i.duree])
        temps_moyen = total_heures / interventions_terminees.count() if interventions_terminees.count() > 0 else 0
    else:
        temps_moyen = 0
    
    # Taux de résolution
    total_incidents = Incident.objects.count()
    incidents_resolus = Incident.objects.filter(etat='resolu').count()
    taux_resolution = (incidents_resolus / total_incidents * 100) if total_incidents > 0 else 0
    
    # Interventions en cours
    interventions_en_cours = interventions.filter(statut='en_cours').count()
    
    # Coût total matériel ce mois
    cout_total = interventions.filter(
        date_debut__gte=debut_mois
    ).aggregate(total=Sum('cout_materiel'))['total'] or 0
    
    # Liste des techniciens
    techniciens = Profile.objects.filter(role='technicien')
    
    # Liste des espaces
    espaces = Espace.objects.all().order_by('nom')
    
    context = {
        'interventions': interventions,
        'techniciens': techniciens,
        'espaces': espaces,
        'temps_moyen': temps_moyen,
        'taux_resolution': round(taux_resolution, 1),
        'interventions_en_cours': interventions_en_cours,
        'cout_total': cout_total,
    }
    
    return render(request, 'admin_interface/interventions_suivi.html', context)