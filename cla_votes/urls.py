"""cla_votes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from cla_auth.views import LoginAuthView

urlpatterns = [
    path("admin/login/", LoginAuthView.as_view(), name='admin:login'),  # Override default login
    path('admin/', admin.site.urls),
    path('auth/', include("cla_auth.urls")),
    path('', include("cla_public.urls")),
    path('', include("cla_bdx.urls")),
    path('', include("cla_ca.urls")),
    path('', include("cla_customvotes.urls")),
    path('enscl/', include("cla_enscl.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Site des votes"

handler400 = 'cla_votes.error_views.error_400'
handler403 = 'cla_votes.error_views.error_403'
handler404 = 'cla_votes.error_views.error_404'
handler500 = 'cla_votes.error_views.error_500'
