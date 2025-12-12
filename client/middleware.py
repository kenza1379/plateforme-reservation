from django.utils.deprecation import MiddlewareMixin
from .models import ActiveSession

class SessionTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            session_key = request.session.session_key
            
            if session_key:
                # Récupérer les infos du device
                user_agent = request.META.get('HTTP_USER_AGENT', 'Inconnu')
                device_info = self.parse_user_agent(user_agent)
                ip_address = self.get_client_ip(request)
                
                # Créer ou mettre à jour la session
                ActiveSession.objects.update_or_create(
                    session_key=session_key,
                    defaults={
                        'user': request.user,
                        'device_info': device_info,
                        'ip_address': ip_address,
                    }
                )
    
    def parse_user_agent(self, user_agent):
        """Parse le user agent pour extraire les infos du device"""
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            if 'Android' in user_agent:
                return '📱 Mobile Android'
            elif 'iPhone' in user_agent or 'iPad' in user_agent:
                return '📱 iPhone/iPad'
            return '📱 Mobile'
        elif 'Windows' in user_agent:
            return '💻 Windows'
        elif 'Macintosh' in user_agent or 'Mac OS' in user_agent:
            return '💻 Mac'
        elif 'Linux' in user_agent:
            return '💻 Linux'
        return '🖥️ Navigateur'
    
    def get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip