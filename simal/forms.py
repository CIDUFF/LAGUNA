from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from .models import *

# class Coleta_agua(forms.ModelForm):
    
#     def __init__(self,*args,**kwargs):

#         super(Coleta_agua, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Fieldset(
#                 'Dados da coleta',
#                 'data_coleta_campo',
#                 'codigo_amostra',
#                 'coletor',
#                 'laboratorio',
#                 'solicitante',
#                 'ponto_coleta'
#             ),
#             ButtonHolder(
#                 Submit('submit', 'Salvar')
#             )
#         )

#     class Meta:

#         model = ProgramaColeta
#         fields = ['data_coleta_campo', 'codigo_amostra', 'coletor', 'laboratorio', 'solicitante', 'ponto_coleta']
#         widgets = {
#             'data_coleta_campo': forms.DateInput(attrs={'type': 'date', 'class': 'flatpickr'}),
#         }
        
#TODO: Fazer form para coleta no campo

# class ColetaCampo (forms.ModelForm):
   