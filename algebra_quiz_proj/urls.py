"""
URL configuration — no admin, no DB.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('quiz.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
