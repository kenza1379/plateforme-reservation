from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from datetime import datetime, time, date
from .models import Espace, Reservation, ActiveSession, PaymentCard, Favori
from .forms import ReservationForm
from django.db import transaction
import random
from django.utils import timezone
from django.http import JsonResponse
from client.utils import envoyer_email_confirmation_paiement
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


# ---------------- Accueil ----------------
def accueil(request):
    espaces = Espace.objects.filter(disponible=True)

    ville = request.GET.get('ville')
    type_espace = request.GET.get('type_espace')
    date_str = request.GET.get('date')

    is_search = bool(ville or type_espace or date_str)

    if ville:
        espaces = espaces.filter(ville__icontains=ville)
    if type_espace:
        espaces = espaces.filter(type_espace=type_espace)
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            espaces = espaces.exclude(reservations__date=date_obj)
        except ValueError:
            pass

    tri = request.GET.get('tri')
    if tri == "prix_asc":
        espaces = espaces.order_by('prix_par_heure')
    elif tri == "prix_desc":
        espaces = espaces.order_by('-prix_par_heure')
    elif tri == "capacite":
        espaces = espaces.order_by('-capacite')

    if not is_search:
        espaces = espaces[:6]
    
    for espace in espaces:
        if espace.equipements:
            espace.equipements_list = [eq.strip() for eq in espace.equipements.split(',') if eq.strip()]
        else:
            espace.equipements_list = []

    favoris_ids = []
    if request.user.is_authenticated:
        favoris_ids = list(Favori.objects.filter(user=request.user).values_list('espace_id', flat=True))

    return render(request, "client/accueil.html", {
        "espaces": espaces,
        "favoris_ids": favoris_ids  
    })


# ---------------- Espaces par catégorie ----------------
def espaces_par_categorie(request, categorie):
    categories_mapping = {
        'reunion': ['reunion'],
        'coworking': ['petite_salle', 'moyenne_salle','brainstorming','espace_detente'],  
        'evenements': ['grande_salle','espace_formation','studio'],
    }
    
    types_espaces = categories_mapping.get(categorie, [categorie])
    espaces = Espace.objects.filter(disponible=True, type_espace__in=types_espaces)
    
    noms_categories = {
        'reunion': 'Salles de réunion',
        'coworking': 'Espaces coworking',
        'evenements': 'Salles d\'événements',
    }
    
    categorie_nom = noms_categories.get(categorie, categorie)
    
    for espace in espaces:
        if espace.equipements:
            espace.equipements_list = [eq.strip() for eq in espace.equipements.split(',') if eq.strip()]
        else:
            espace.equipements_list = []

    favoris_ids = []
    if request.user.is_authenticated:
        favoris_ids = list(Favori.objects.filter(user=request.user).values_list('espace_id', flat=True))
    
    context = {
        'espaces': espaces,
        'categorie': categorie,
        'categorie_nom': categorie_nom,
        'total': espaces.count(),
        'favoris_ids': favoris_ids  
    }
    
    return render(request, "client/espaces_categorie.html", context)


# ---------------- Détail Espace ----------------
def detail_espace(request, espace_id):
    espace = get_object_or_404(Espace, id=espace_id)

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter pour réserver cet espace.")
            return redirect(f"/users/login/?next=/espace/{espace_id}/")

        form = ReservationForm(request.POST, espace=espace)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            selected_time = form.cleaned_data['heure_debut']
            selected_datetime = datetime.combine(selected_date, selected_time)
            
            if selected_datetime < datetime.now():
                messages.error(request, "Vous ne pouvez pas réserver dans le passé.")
                favoris_ids = []
                if request.user.is_authenticated:
                    favoris_ids = list(Favori.objects.filter(user=request.user).values_list('espace_id', flat=True))
                
                return render(request, 'client/detail_espace.html', {
                    "espace": espace,
                    "form": form,
                    "favoris_ids": favoris_ids
                })
            
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.espace = espace
            reservation.prix_total = espace.prix_par_heure * reservation.duree_heures
            reservation.save()

            return redirect('mes_reservations')
        else:
            messages.error(request, "Impossible de réserver : vérifiez les informations saisies.")
    else:
        form = ReservationForm(espace=espace)

    favoris_ids = []
    if request.user.is_authenticated:
        favoris_ids = list(Favori.objects.filter(user=request.user).values_list('espace_id', flat=True))

    return render(request, 'client/detail_espace.html', {
        "espace": espace,
        "form": form,
        "favoris_ids": favoris_ids 
    })


# ---------------- Authentification ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà pris.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("accueil")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or 'accueil'
        
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(next_url)

        messages.error(request, "Identifiants invalides.")
        return redirect("login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("accueil")


# ---------------- Mon compte ----------------
@login_required
def mon_compte(request):
    user = request.user

    if request.method == 'POST':
        profile = user.profile

        fields_map = {
            'first_name': lambda val: setattr(user, 'first_name', val),
            'last_name': lambda val: setattr(user, 'last_name', val),
            'email': lambda val: setattr(user, 'email', val),
            'public_name': lambda val: setattr(profile, 'public_name', val),
            'phone': lambda val: setattr(profile, 'phone', val),
            'birth_date': lambda val: setattr(profile, 'birth_date', val or None),
            'nationality': lambda val: setattr(profile, 'nationality', val),
            'gender': lambda val: setattr(profile, 'gender', val),
            'address': lambda val: setattr(profile, 'address', val),
            'postal_code': lambda val: setattr(profile, 'postal_code', val),  
            'city': lambda val: setattr(profile, 'city', val),  
        }

        for field, setter in fields_map.items():
            if field in request.POST:
                setter(request.POST.get(field, '').strip())

        profile.save()
        user.save()
        return redirect('mon_compte')

    return render(request, 'client/mon_compte.html', {'user': user})


# ---------------- Sécurité ----------------
@login_required
def security_settings(request):
    active_sessions = ActiveSession.objects.filter(user=request.user)
    context = {'active_sessions': active_sessions, 'current_session_key': request.session.session_key}
    return render(request, 'client/security_settings.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not new_password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
        elif new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif len(new_password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

    return redirect('security_settings')


@login_required
def logout_session(request, session_key):
    if session_key == request.session.session_key:
        messages.error(request, "Vous ne pouvez pas déconnecter votre session actuelle.")
        return redirect('security_settings')

    try:
        Session.objects.get(session_key=session_key).delete()
    except Session.DoesNotExist:
        pass

    ActiveSession.objects.filter(user=request.user, session_key=session_key).delete()
    return redirect('security_settings')


@login_required
def logout_all_sessions(request):
    current_session = request.session.session_key
    sessions = ActiveSession.objects.filter(user=request.user).exclude(session_key=current_session)
    count = sessions.count()
    for s in sessions:
        try:
            Session.objects.get(session_key=s.session_key).delete()
        except Session.DoesNotExist:
            pass
    sessions.delete()

    if count:
        messages.success(request, f"{count} session(s) déconnectée(s).")
    return redirect('security_settings')


@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get("confirm_password")
        if not check_password(password, request.user.password):
            messages.error(request, "Mot de passe incorrect.")
            return redirect("security_settings")

        user = request.user
        logout(request)
        user.delete()
        return redirect("accueil")

    return redirect("security_settings")


# ---------------- Paiements ----------------
@login_required
def payment_methods(request):
    user = request.user
    payment_cards = PaymentCard.objects.filter(user=user)
    default_card_id = user.profile.default_card.id if user.profile.default_card else None
    return render(request, "client/payment_methods.html", {
        "payment_cards": payment_cards,
        "default_card_id": default_card_id
    })


@login_required
def add_card(request):
    if request.method == "POST":
        card_name = request.POST.get('cardName', '').strip()
        card_number = request.POST.get('cardNumber', '').strip()
        expiry = request.POST.get('expiryDate', '').strip()
        cvv = request.POST.get('cvv', '').strip()

        if not all([card_name, card_number, expiry, cvv]):
            messages.error(request, "Tous les champs sont requis.")
            return redirect('payment_methods')

        last_four = card_number.replace(" ", "")[-4:]
        card_type = detect_card_type(card_number)

        PaymentCard.objects.create(
            user=request.user,
            name=card_name,
            last_four=last_four,
            expiry=expiry,
            type=card_type
        )

        if not request.user.profile.default_card:
            request.user.profile.default_card = PaymentCard.objects.filter(user=request.user).last()
            request.user.profile.save()

        return redirect('payment_methods')

    return redirect('payment_methods')


@login_required
def delete_card(request, card_id):
    card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
    if request.user.profile.default_card and request.user.profile.default_card.id == card.id:
        request.user.profile.default_card = None
        request.user.profile.save()
    card.delete()
    return redirect("payment_methods")


@login_required
def set_default_card(request, card_id):
    card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
    request.user.profile.default_card = card
    request.user.profile.save()
    return redirect("payment_methods")


def detect_card_type(card_number):
    cleaned = card_number.replace(" ", "")
    if cleaned.startswith("4"):
        return "Visa"
    elif cleaned[:2] in ["51", "52", "53", "54", "55"]:
        return "Mastercard"
    elif cleaned[:2] in ["34", "37"]:
        return "AMEX"
    elif cleaned.startswith("6"):
        return "Discover"
    elif cleaned.startswith("35"):
        return "JCB"
    elif cleaned[:2] in ["30", "36", "38"]:
        return "Diners"
    elif cleaned.startswith("62"):
        return "UnionPay"
    else:
        return "CB"


# ---------------- Réservations ----------------
@login_required
def reserver_espace(request, espace_id):
    espace = get_object_or_404(Espace, id=espace_id)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        heure_debut_str = request.POST.get('heure_debut')
        duree = int(request.POST.get('duree_heures', 1))

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            heure_obj = datetime.strptime(heure_debut_str, "%H:%M").time()
            
            if date_obj < date.today():
                messages.error(request, "Vous ne pouvez pas réserver une date passée.")
                return redirect('detail_espace', espace_id=espace.id)
            
            selected_datetime = datetime.combine(date_obj, heure_obj)
            if selected_datetime < datetime.now():
                messages.error(request, "Vous ne pouvez pas réserver dans le passé.")
                return redirect('detail_espace', espace_id=espace.id)
            
            prix_total = espace.prix_par_heure * duree

            conflict = Reservation.objects.filter(
                espace=espace,
                date=date_obj,
                heure_debut=heure_obj
            ).exists()

            if conflict:
                messages.error(request, "Ce créneau est déjà réservé.")
            else:
                Reservation.objects.create(
                    user=request.user,
                    espace=espace,
                    date=date_obj,
                    heure_debut=heure_obj,
                    duree_heures=duree,
                    prix_total=prix_total
                )
                return redirect('mes_reservations')
                
        except ValueError:
            messages.error(request, "Format de date ou heure invalide.")

    return redirect('detail_espace', espace_id=espace.id)


@login_required
def mes_reservations(request):
    reservations = (
        Reservation.objects
        .filter(user=request.user)
        .select_related('espace')
        .order_by('-date', '-heure_debut')
    )

    total_count = reservations.count()
    confirmee_count = reservations.filter(status='confirmee').count()
    en_attente_count = reservations.filter(status='en_attente').count()
    annulee_count = reservations.filter(status='annulee').count()

    context = {
        'reservations': reservations,
        'total_count': total_count,
        'confirmee_count': confirmee_count,
        'en_attente_count': en_attente_count,
        'annulee_count': annulee_count,
    }

    return render(request, "client/mes_reservations.html", context)


@login_required
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, "client/reservation_detail.html", {'reservation': reservation})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        reservation.status = "annulee"
        reservation.save()

        subject = "Confirmation d'annulation de votre réservation"
        html_message = render_to_string('client/emails/reservation_cancelled.html', {
            'user': request.user,
            'reservation': reservation,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = reservation.user.email

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

        return redirect('mes_reservations')

    return redirect('reservation_detail', reservation_id=reservation_id)


# ---------------- Paiement ----------------
@login_required
def payment_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if reservation.status != 'en_attente':
        messages.error(request, "Cette réservation ne peut pas être payée.")
        return redirect('reservation_detail', reservation_id=reservation.id)
    
    payment_cards = PaymentCard.objects.filter(user=request.user)
    default_card = request.user.profile.default_card
    
    context = {
        'reservation': reservation,
        'payment_cards': payment_cards,
        'default_card': default_card,
    }
    
    return render(request, 'client/payment_page.html', context)


@login_required
def process_payment(request, reservation_id):
    if request.method != 'POST':
        return redirect('payment_page', reservation_id=reservation_id)
    
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if reservation.status != 'en_attente':
        messages.error(request, "Cette réservation a déjà été traitée.")
        return redirect('mes_reservations')
    
    payment_method = request.POST.get('payment_method')
    
    if payment_method == 'existing_card':
        card_id = request.POST.get('card_id')
        
        if not card_id:
            messages.error(request, "Veuillez sélectionner une carte.")
            return redirect('payment_page', reservation_id=reservation.id)
        
        card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
        success = simulate_payment(reservation, card)
        
        if success:
            with transaction.atomic():
                reservation.status = 'confirmee'  
                reservation.paid = True
                reservation.payment_method = f"{card.type} •••• {card.last_four}"
                reservation.payment_date = timezone.now()
                reservation.save()
            
            envoyer_email_confirmation_paiement(reservation)
            return redirect('reservation_detail', reservation_id=reservation.id)
        else:
            messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
            return redirect('payment_page', reservation_id=reservation.id)
    
    elif payment_method == 'new_card':
        card_name = request.POST.get('card_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        expiry = request.POST.get('expiry', '').strip()
        cvv = request.POST.get('cvv', '').strip()
        save_card = request.POST.get('save_card') == 'on'
        
        if not all([card_name, card_number, expiry, cvv]):
            messages.error(request, "Tous les champs sont requis.")
            return redirect('payment_page', reservation_id=reservation.id)
        
        card_number_clean = card_number.replace(" ", "")
        if len(card_number_clean) < 13 or len(card_number_clean) > 19:
            messages.error(request, "Numéro de carte invalide.")
            return redirect('payment_page', reservation_id=reservation.id)
        
        if len(cvv) < 3 or len(cvv) > 4:
            messages.error(request, "CVV invalide.")
            return redirect('payment_page', reservation_id=reservation.id)
        
        last_four = card_number_clean[-4:]
        card_type = detect_card_type(card_number)
        
        temp_card = type('obj', (object,), {
            'type': card_type,
            'last_four': last_four
        })()
        
        success = simulate_payment(reservation, temp_card)
        
        if success:
            with transaction.atomic():
                if save_card:
                    new_card = PaymentCard.objects.create(
                        user=request.user,
                        name=card_name,
                        last_four=last_four,
                        expiry=expiry,
                        type=card_type
                    )
                    
                    if not request.user.profile.default_card:
                        request.user.profile.default_card = new_card
                        request.user.profile.save()
                
                reservation.paid = True
                reservation.status = 'confirmee'  
                reservation.payment_date = timezone.now()
                reservation.payment_method = f"{card_type} •••• {last_four}" 
                reservation.save()
            
            envoyer_email_confirmation_paiement(reservation)
            return redirect('reservation_detail', reservation_id=reservation.id)
        else:
            messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
            return redirect('payment_page', reservation_id=reservation.id)
    
    messages.error(request, "Méthode de paiement invalide.")
    return redirect('payment_page', reservation_id=reservation.id)


def simulate_payment(reservation, card):
    import time
    
    time.sleep(0.3)
    
    if not card or not card.last_four:
        return False
    
    success = random.random() < 0.95
    
    if success:
        reservation.payment_date = timezone.now()
        return True
    
    return False


# ---------------- Favoris ----------------
@login_required
def mes_favoris(request):
    favoris = Favori.objects.filter(user=request.user).select_related('espace')
    
    espaces_favoris = [fav.espace for fav in favoris]
    favoris_ids = [fav.espace.id for fav in favoris]
    
    context = {
        'espaces_favoris': espaces_favoris,
        'favoris_ids': favoris_ids,
        'total_favoris': len(espaces_favoris)
    }
    
    return render(request, 'client/mes_favoris.html', context)


@login_required
def toggle_favori(request, espace_id):
    espace = get_object_or_404(Espace, id=espace_id)
    
    favori = Favori.objects.filter(user=request.user, espace=espace).first()
    
    if favori:
        favori.delete()
        is_favorite = False
        message = f"{espace.nom} retiré des favoris"
    else:
        Favori.objects.create(user=request.user, espace=espace)
        is_favorite = True
        message = f"{espace.nom} ajouté aux favoris"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'accueil'))