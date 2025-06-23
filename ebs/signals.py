from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Dispositivo, Historico
from django.contrib.auth.models import User
from threading import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

# Middleware para capturar o usuário
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user
        response = self.get_response(request)
        return response

# Registra criação e alterações
@receiver(post_save, sender=Dispositivo)
def registrar_historico(sender, instance, created, **kwargs):
    usuario = get_current_user()
    if created:
        acao = f"Criou dispositivo {instance.numero_serial}"
    else:
        acao = f"Editou dispositivo {instance.numero_serial}"
    Historico.objects.create(usuario=usuario, dispositivo=instance, acao=acao)

@receiver(pre_save, sender=Dispositivo)
def salvar_estado_anterior(sender, instance, **kwargs):
    try:
        instance._dispositivo_antigo = Dispositivo.objects.get(pk=instance.pk)
    except Dispositivo.DoesNotExist:
        instance._dispositivo_antigo = None

@receiver(post_save, sender=Dispositivo)
def registrar_historico(sender, instance, created, **kwargs):
    usuario = get_current_user()

    if created:
        acao = f"Criou dispositivo {instance.numero_serial}"
    else:
        dispositivo_antigo = getattr(instance, '_dispositivo_antigo', None)

        if dispositivo_antigo:
            mudou_cliente = dispositivo_antigo.cliente != instance.cliente
            mudou_posto = dispositivo_antigo.posto != instance.posto

            if mudou_cliente or mudou_posto:
                nome_cliente_antigo = dispositivo_antigo.cliente.nome
                nome_posto_antigo = dispositivo_antigo.posto.nome
                nome_cliente_novo = instance.cliente.nome
                nome_posto_novo = instance.posto.nome

                acao = (
                    f"Dispositivo {instance.numero_serial} estava no posto {nome_posto_antigo} "
                    f"no cliente {nome_cliente_antigo} e foi movido para o posto {nome_posto_novo} "
                    f"no cliente {nome_cliente_novo}"
                )
            else:
                acao = f"Editou dispositivo {instance.numero_serial}"
        else:
            acao = f"Editou dispositivo {instance.numero_serial}"

    Historico.objects.create(usuario=usuario, dispositivo=instance, acao=acao)
