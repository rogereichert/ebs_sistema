from django import template
from ebs.models import Cliente

register = template.Library()

@register.filter
def lookup_cliente_nome(cliente_id):
    try:
        return Cliente.objects.get(id=cliente_id).nome
    except Cliente.DoesNotExist:
        return "Cliente não encontrado"
