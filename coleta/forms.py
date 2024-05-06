from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from .models import ProgramaColeta

class Coleta_agua(forms.ModelForm):
    """
    A form for collecting water samples.

    This form is used to collect data related to water samples, including the date of collection,
    the sample code, the collector, the laboratory, the requester, and the collection point.

    Attributes:
        model (Model): The model class associated with the form.
        fields (list): The fields to include in the form.
        widgets (dict): The widgets to use for rendering form fields.

    """
    
    def __init__(self,*args,**kwargs):
        """
        Constructor for the ProgramaColeta form.

        This method initializes the form with a custom layout using the crispy_forms helper.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        super(Coleta_agua, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados da coleta',
                'data_coleta_campo',
                'codigo_amostra',
                'coletor',
                'laboratorio',
                'solicitante',
                'ponto_coleta'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar')
            )
        )

    class Meta:
        """
        Meta class for defining metadata options for the ProgramaColeta form.
        """
        model = ProgramaColeta
        fields = ['data_coleta_campo', 'codigo_amostra', 'coletor', 'laboratorio', 'solicitante', 'ponto_coleta']
        widgets = {
            'data_coleta_campo': forms.DateInput(attrs={'type': 'date', 'class': 'flatpickr'}),
        }
        
#TODO: Fazer form para coleta no campo

# class ColetaCampo (forms.ModelForm):
   