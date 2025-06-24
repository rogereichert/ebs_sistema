from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Posto, MetodoAquisicao, Dispositivo, Historico, Ticket, ComentarioTicket
from .forms import DispositivoForm, ClienteForm, PostoForm, TicketForm

# ------------------------
# Cliente Admin
# ------------------------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_per_page = 50
    list_display = ('id', 'nome', 'cnpj', 'cidade', 'estado')
    search_fields = ('nome', 'cnpj')

# ------------------------
# Posto Admin
# ------------------------
@admin.register(Posto)
class PostoAdmin(admin.ModelAdmin):
    form = PostoForm
    list_per_page = 50
    list_display = ('id', 'nome', 'cep', 'endereco', 'cidade', 'estado')
    list_filter = ('cliente',)
    search_fields = ('nome',)
    list_display_links = ('id', 'nome',)

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

# ------------------------
# Metodo Aquisição Admin
# ------------------------
@admin.register(MetodoAquisicao)
class MetodoAquisicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)

# ------------------------
# Dispositivo Admin
# ------------------------
@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    form = DispositivoForm
    list_per_page = 50

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
    search_fields = ('numero_serial', 'imei', 'numero')
    list_editable = ('dados', 'online', 'leitura', 'ligacao', 'base', 'bateria', 'fonte')
    list_select_related = ('cliente', 'posto', 'metodo_aquisicao')

    def link_pdf(self, obj):
        return format_html('<a href="/dispositivos/pdf/dispositivo/{}/" target="_blank">📄 PDF</a>', obj.id)

    link_pdf.short_description = "Relatório"

# ------------------------
# Histórico Admin
# ------------------------
@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'dispositivo', 'data_hora')
    list_filter = ('usuario', 'data_hora')
    search_fields = ('acao', 'dispositivo__numero_serial')

# ------------------------
# Comentários Inline em Ticket
# ------------------------
class ComentarioInline(admin.TabularInline):
    model = ComentarioTicket
    extra = 1
    readonly_fields = ('data_criada', 'autor')
    fields = ('mensagem', 'autor', 'data_criada')

    def save_new_objects(self, formset, commit=True):
        for form in formset.forms:
            if not form.cleaned_data:
                continue
            obj = form.save(commit=False)
            if not obj.autor_id:
                obj.autor = formset.request.user
            if commit:
                obj.save()
        formset.save_m2m()

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

# ------------------------
# Ticket Admin
# ------------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketForm

    # Campos exibidos na lista de tickets
    list_display = (
        'titulo_formatado', 'cliente', 'prioridade', 'status',
        'data_abertura', 'data_limite_sla', 'data_conclusao',
        'status_sla', 'atribuido_para'
    )
    list_filter = ('cliente', 'prioridade', 'status', 'categoria', 'sla_vencido')
    search_fields = ('titulo', 'descricao', 'cliente__nome', 'posto__nome', 'dispositivo__numero_serial')
    autocomplete_fields = ('cliente', 'posto', 'dispositivo', 'atribuido_para')
    readonly_fields = ('data_abertura', 'data_limite_sla', 'sla_vencido')

    inlines = [ComentarioInline]

    fieldsets = (
        ("Informações do Chamado", {
            "fields": ("titulo", "descricao", "cliente", "posto", "dispositivo")
        }),
        ("Controle", {
            "fields": ("prioridade", "categoria", "status", "usuario_solicitante", "atribuido_para")
        }),
        ("SLA", {
            "fields": ("data_abertura", "data_limite_sla", "data_conclusao", "sla_vencido")
        })
    )
    
    def titulo_formatado(self, obj):
        return format_html(
            '<span style="white-space: nowrap; display: inline-block; min-width: 200px;">{}</span>',
            obj.titulo
        )
        titulo_formatado.short_description = 'Título'

    # Exibe ícone e texto indicando se o SLA foi cumprido
    def status_sla(self, obj):
        """
        Retorna ícone com texto e evita quebra de linha na célula da tabela.
        """
        style = "white-space: nowrap; display: inline-block; min-width: 120px;"
        if obj.sla_vencido:
            return format_html(f'<span style="{style} color: red;">&#10060; Vencido</span>')
        return format_html(f'<span style="{style} color: limegreen;">&#10004; Dentro do prazo</span>')
        status_sla.short_description = "SLA"
