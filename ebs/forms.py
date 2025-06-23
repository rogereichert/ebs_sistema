from dal import autocomplete
from django import forms
from .models import Dispositivo, Cliente, Posto, Ticket

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = '__all__'
        widgets = {
            'posto': autocomplete.ModelSelect2(
                url='posto-autocomplete',
                forward=['cliente']  # diz que depende do campo cliente
            ),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'style': 'width: 600px;'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
            'cnpj': forms.TextInput(attrs={
                'placeholder': '00.000.000/0000-00',
                'data-mask': '00.000.000/0000-00',
                'style': 'width: 500px;',
            }),
            # 'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, Avenida, etc.'}),
            'bairro': forms.TextInput(attrs={'placeholder': 'Bairro do posto'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Cidade do posto'}),
            'estado': forms.TextInput(attrs={'placeholder': 'Estado do posto'}),
        }
        
class PostoForm(forms.ModelForm):
    class Meta:
        model = Posto
        fields = '__all__'
        widgets = {
            # 'cep': forms.TextInput(attrs={'data-mask': '00000-000', 'placeholder': '00000-000'}),
            # 'cep': forms.TextInput(attrs={'placeholder': 'CEP'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, Avenida, etc.'}),
            'bairro': forms.TextInput(attrs={'placeholder': 'Bairro do posto'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Cidade do posto'}),
            'estado': forms.TextInput(attrs={'placeholder': 'Estado do posto'}),

        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        widgets = {
            'posto': autocomplete.ModelSelect2(
                url='posto-autocomplete',
                forward=['cliente']
            ),
            'dispositivo': autocomplete.ModelSelect2(
                url='dispositivo-autocomplete',
                forward=['posto']
            ),
        }
