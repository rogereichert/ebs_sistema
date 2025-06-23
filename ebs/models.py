from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Modelo para representar um cliente
# Cada cliente tem um nome, CNPJ, CEP, endereço, bairro, cidade e estado
class Cliente(models.Model):
    nome = models.CharField(max_length=100) # Nome do cliente
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True) # CNPJ do cliente
    cep = models.CharField(max_length=9, blank=True, null=True) # CEP do cliente
    endereco = models.CharField(max_length=255, blank=True, null=True) # Endereço do cliente
    bairro = models.CharField(max_length=100, blank=True, null=True) # Bairro do cliente
    cidade = models.CharField(max_length=100, blank=True, null=True) # Cidade do cliente
    estado = models.CharField(max_length=2, blank=True, null=True) # Estado do cliente
    
    def __str__(self):
        return self.nome
    
# Modelo para representar um posto do cliente
class Posto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE) # Relacionamento com o cliente
    nome = models.CharField(max_length=100) # Nome do posto
    cep = models.CharField(max_length=9, blank=True, null=True) # CEP do cliente
    endereco = models.CharField(max_length=255, blank=True, null=True) # Endereço do cliente
    bairro = models.CharField(max_length=100, blank=True, null=True) # Bairro do cliente
    cidade = models.CharField(max_length=100, blank=True, null=True) # Cidade do cliente
    estado = models.CharField(max_length=2, blank=True, null=True) # Estado do cliente
    status = models.CharField(max_length=20, default='Ativo') # Status do posto (ativo ou inativo)
    
    def __str__(self): 
        return self.nome

# Modelo para representar um método de aquisição
# Cada método de aquisição tem um nome
class MetodoAquisicao(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Método de Aquisição"
        verbose_name_plural = "Método de Aquisição"
    
# Modelo para representar um dispositivo
# Cada dispositivo está associado a um cliente e a um posto
class Dispositivo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    posto = models.ForeignKey(Posto, on_delete=models.CASCADE)
    numero_serial = models.CharField(max_length=6, unique=True)
    
    CONFIGURACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=CONFIGURACAO_CHOICES,
        default='ATIVO',
        verbose_name='Status do Dispositivo',
    )
    
    data_entrada = models.DateField(null=True, blank=True)
    data_saida = models.DateField(null=True, blank=True)

    CONFIGURACAO_CHOICES = [
        ('VIVO', 'Vivo'),
        ('CLARO', 'Claro'),
        ('TIM', 'Tim'),
        ('OI', 'Oi'),
        ('ARQIA', 'Arquia'),
        ('OUTRO', 'Outro'),
    ]
    
    configuracao = models.CharField(
        max_length=20,
        choices=CONFIGURACAO_CHOICES,
        default='VIVO',
        blank=True,
        null=True,
    )
    
    imei = models.CharField(max_length=15, blank=True)
    numero = models.CharField(max_length=15, blank=True)
    metodo_aquisicao = models.ForeignKey(MetodoAquisicao, on_delete=models.SET_NULL, null=True, default=3)
    
    # Campos de checkbox (0 = false, 1 = verdadeiro) )
    dados = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    leitura = models.BooleanField(default=False)
    ligacao = models.BooleanField(default=False)
    base = models.BooleanField(default=False)
    bateria = models.BooleanField(default=False)
    fonte = models.BooleanField(default=False)
    
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Dispositivo {self.numero_serial}"
    
class Historico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    acao = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.acao} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"