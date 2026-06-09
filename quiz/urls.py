from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/generate-question/', views.api_generate_question, name='api_generate_question'),
    path('api/check-answer/', views.api_check_answer, name='api_check_answer'),
]
