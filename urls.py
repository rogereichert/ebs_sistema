from django.urls import path
from .views import gerar_pdf_dispositivo

urlpatterns = [
    path('pdf/dispositivo/<int:dispositivo_id>/', gerar_pdf_dispositivo, name="pdf_dispositivo"),
]
