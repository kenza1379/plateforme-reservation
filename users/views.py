from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from client.models import Profile

User = get_user_model()


def login_user(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('identifier')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = None
        user_obj = User.objects.filter(email=email_or_username).first()
        
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = authenticate(request, username=email_or_username, password=password)

        if user is not None:
            login(request, user)

            if not remember:
                request.session.set_expiry(0)

            try:
                role = user.profile.role
            except Profile.DoesNotExist:
                role = 'client'

            if role == 'admin' or user.is_staff:
                return redirect('admin_interface:dashboard')
            elif role == 'technicien':
                return redirect('tech_interface:dashboard')
            else:
                return redirect('accueil')
        else:
            return render(request, 'users/login.html', {
                'error': 'Identifiants incorrects',
                'identifier': email_or_username
            })

    return render(request, 'users/login.html')


def signup_user(request, role='client'):
    if role == 'technicien' and (not request.user.is_authenticated or not request.user.is_staff):
        return redirect('login')

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        terms = request.POST.get('terms')

        if role == 'client' and not terms:
            return render(request, 'users/signup.html', {
                'error': "Vous devez accepter les conditions d'utilisation",
                'fullname': fullname,
                'email': email
            })

        if password != confirm_password:
            return render(request, 'users/signup.html', {
                'error': "Les mots de passe ne correspondent pas",
                'fullname': fullname,
                'email': email
            })

        if len(password) < 8:
            return render(request, 'users/signup.html', {
                'error': "Le mot de passe doit contenir au moins 8 caractères",
                'fullname': fullname,
                'email': email
            })

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'users/signup.html', {
                'error': "Un compte avec cet email existe déjà",
                'fullname': fullname,
                'email': email
            })

        try:
            name_parts = fullname.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=(role=='admin')  
            )

            Profile.objects.create(user=user, role=role)

            if role == 'client':
                login(request, user)
                return redirect('accueil')
            else:
                return redirect('admin_interface:techniciens_list')

        except Exception as e:
            return render(request, 'users/signup.html', {
                'error': f"Une erreur est survenue : {str(e)}",
                'fullname': fullname,
                'email': email
            })

    return render(request, 'users/signup.html', {'role': role})


def logout_user(request):
    logout(request)
    return redirect('login')


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            context = {
                'user': user,
                'uid': uid,
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
            }
            
            subject = 'Réinitialisation de votre mot de passe'
            html_message = render_to_string('users/password_reset_email.html', context)
            
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            return redirect('password_reset_done')
        except Exception:
            return redirect('login')
    
    return redirect('login')


def password_reset_done(request):
    return render(request, 'users/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('new_password1')
            password2 = request.POST.get('new_password2')
            
            if password1 and password1 == password2:
                if len(password1) < 8:
                    return render(request, 'users/password_reset_confirm.html', {
                        'validlink': True,
                        'error': 'Le mot de passe doit contenir au moins 8 caractères.'
                    })
                
                user.set_password(password1)
                user.save()
                return redirect('password_reset_complete')
            else:
                return render(request, 'users/password_reset_confirm.html', {
                    'validlink': True,
                    'error': 'Les mots de passe ne correspondent pas.'
                })
        
        return render(request, 'users/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'users/password_reset_confirm.html', {'validlink': False})


def password_reset_complete(request):
    return render(request, 'users/password_reset_complete.html')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)