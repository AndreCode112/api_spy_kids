from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    """View customizada de login"""
    template_name = 'videos/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('video_gallery')
