from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime

def envoyer_email_confirmation_paiement(reservation):
    """
    Envoie un email de confirmation de paiement au client
    """
    try:
        user = reservation.user
        
        # Contexte avec les bonnes données du modèle
        context = {
            'client_nom': user.get_full_name() or user.username,
            'espace_nom': reservation.espace.nom,
            'date': reservation.date.strftime('%d %B %Y'),
            'heure_debut': reservation.heure_debut.strftime('%H:%M'),
            'heure_fin': reservation.heure_fin.strftime('%H:%M'),  # Propriété calculée !
            'duree': reservation.duree_heures,
            'adresse': f"{reservation.espace.adresse}, {reservation.espace.ville}" if reservation.espace.adresse else reservation.espace.ville,
            'prix_total': reservation.prix_total,
            'numero_reservation': reservation.id,
        }
        
        # Générer l'email HTML depuis le template
        html_message = render_to_string('client/emails/confirmation_paiement.html', context)
        
        # Message texte simple (fallback)
        plain_message = f"""
Bonjour {context['client_nom']},

Votre réservation est confirmée !

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Espace : {context['espace_nom']}
📅 Date : {context['date']}
🕒 Horaire : {context['heure_debut']} - {context['heure_fin']}
⏱️ Durée : {context['duree']}h
📍 Adresse : {context['adresse']}
💰 Montant payé : {context['prix_total']}€

Numéro de réservation : #{context['numero_reservation']}

Nous vous attendons avec plaisir !

Cordialement,
L'équipe PointPro
"""
        
        # Envoyer l'email
        send_mail(
            subject=f'✓ Réservation confirmée - {context["espace_nom"]}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Email envoyé avec succès à {user.email}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {str(e)}")
        import traceback
        traceback.print_exc()  # Affiche l'erreur complète pour debugger
        return False