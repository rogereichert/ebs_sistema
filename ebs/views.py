import os
import base64
from dal import autocomplete
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Dispositivo, Historico, Posto
import os
from django.conf import settings

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