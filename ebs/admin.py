from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente , Posto, MetodoAquisicao, Dispositivo, Historico
from .forms import DispositivoForm, ClienteForm, PostoForm


# Register your models here.

# Registro do modelo Cliente no admin do Django
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_per_page = 50  # ou 100, 200, etc.
    list_display = ('id', 'nome', 'cnpj', 'cidade', 'estado')
    search_fields = ('nome', 'cnpj')
    
# Registro do modelo Posto no admin do Django
@admin.register(Posto)
class PostoAdmin(admin.ModelAdmin):
    form = PostoForm
    list_per_page = 50  # ou 100, 200, etc.
    list_display = ('id', 'nome', 'cep', 'endereco', 'cidade', 'estado')
    list_filter = ('cliente',)
    search_fields = ('nome',)
    list_display_links = ('id','nome',)
    
    # Preenche automaticamente o campo "cliente" no formulário de criação
    def get_changeform_initial_data(self, request):
        cliente_id = request.GET.get('cliente')
        if cliente_id:
            return {'cliente': cliente_id}
        return super().get_changeform_initial_data(request)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data'):
            cliente_id = request.GET.get('cliente__id__exact')
            if cliente_id:
                add_url = f"add/?cliente={cliente_id}"
                response.context_data['add_url'] = add_url
        return response

# Registro do modelo Dispositivo no admin do Django
@admin.register(MetodoAquisicao)
class MetodoAquisicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)
    
# Registro do modelo Dispositivo no admin do Django
@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    form = DispositivoForm # configura a paginação
    list_per_page = 50  # ou 100, 200, etc.
    
    fieldsets = (
        ("Dados Gerais", {
            "fields": ("numero_serial", "cliente", "posto", "status", "data_entrada", "data_saida")
        }),
        ("Configurações Técnicas", {
            "fields": ("configuracao", "imei", "numero", "metodo_aquisicao")
        }),
        ("Sinais e Estado", {
            "fields": ("dados", "online", "leitura", "ligacao", "base", "bateria", "fonte")
        }),
        ("Observações", {
            "fields": ("observacoes",)
        }),
    )
    
    list_display = ('numero_serial', 'cliente', 'posto', 'link_pdf', 'dados', 'online', 'leitura', 'ligacao', 'base', 'bateria', 'fonte')
    list_filter = ('cliente', 'posto', 'metodo_aquisicao', 'online', 'bateria')
    search_fields = ('numero_serial', 'imei', 'numero',)
    list_editable = ('dados', 'online', 'leitura', 'ligacao', 'base', 'bateria', 'fonte')
    list_select_related = ('cliente', 'posto', 'metodo_aquisicao')
    
    def link_pdf(self, obj):
        return format_html('<a href="/dispositivos/pdf/dispositivo/{}/" target="_blank">📄 PDF</a>', obj.id)
    
    link_pdf.short_description = "Relatório"

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'dispositivo', 'data_hora')
    list_filter = ('usuario', 'data_hora')
    search_fields = ('acao', 'dispositivo__numero_serial')

    