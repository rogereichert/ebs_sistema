import os
import base64
from dal import autocomplete
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Dispositivo, Historico, Posto, Cliente, Ticket
import os
from django.conf import settings
from django.shortcuts import render
from django.db.models import Avg, Count
from datetime import datetime
from django.db import models

class PostoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Posto.objects.all()

        cliente_id = self.forwarded.get('cliente', None)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)

        return qs
    
def gerar_pdf_dispositivo(request, dispositivo_id):
    dispositivo = Dispositivo.objects.select_related("cliente", "posto").get(id=dispositivo_id)
    historicos = Historico.objects.filter(dispositivo=dispositivo).order_by('-data_hora')

    # Caminho da imagem
    logo_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'imagens', 'ebsbrasil_logo.jpg')

    # Convertendo imagem para base64
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    template = get_template("pdf/dispositivo_detalhes.html")
    html = template.render({
        "dispositivo": dispositivo,
        "historicos": historicos,
        "logo_base64": logo_base64
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{dispositivo.numero_serial}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    return response if not pisa_status.err else HttpResponse("Erro ao gerar PDF", status=500)

class PostoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Posto.objects.all()
        cliente_id = self.forwarded.get('cliente')
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        return qs

class DispositivoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Dispositivo.objects.all()
        posto_id = self.forwarded.get('posto')
        if posto_id:
            qs = qs.filter(posto_id=posto_id)
        return qs

def sla_dashboard(request):
    tickets = Ticket.objects.all()

    total = tickets.count()
    vencidos = tickets.filter(sla_vencido=True).count()
    dentro_prazo = total - vencidos
    resolvidos = tickets.filter(status='resolvido').count()
    abertos = tickets.filter(status='aberto').count()
    em_andamento = tickets.filter(status='em_andamento').count()

    tempo_medio = tickets.filter(
        status='resolvido', 
        data_conclusao__isnull=False
    ).annotate(
        duracao=models.F('data_conclusao') - models.F('data_abertura')
    ).aggregate(media=Avg('duracao'))['media']

    return render(request, 'dashboard/sla_dashboard.html', {
        'total': total,
        'vencidos': vencidos,
        'dentro_prazo': dentro_prazo,
        'resolvidos': resolvidos,
        'abertos': abertos,
        'em_andamento': em_andamento,
        'tempo_medio': tempo_medio,
        'grafico_sla': [dentro_prazo, vencidos],
        'grafico_status': [abertos, em_andamento, resolvidos],
    })