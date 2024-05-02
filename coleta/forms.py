from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from .models import Coleta_lagoa



#TODO: #3 Criar forms para cadastro de pessoas e laboratórios
class Coleta_agua(forms.ModelForm):
    """
    A form for collecting water samples.

    This form is used to collect data related to water samples, including the date of collection,
    the location of collection, the person responsible for the collection, and various water quality parameters.

    Attributes:
        model (Model): The model class associated with the form.
        fields (list): The fields to include in the form.
        widgets (dict): The widgets to use for rendering form fields.

    """
    
    def __init__(self,*args,**kwargs):
        """
        Constructor for the Coleta_lagoa form.

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
                'data_coleta',
                'local_coleta',
                'responsavel_coleta',
                'pH',
                'temperatura',
                'turbidez',
                'oxigenio_dissolvido',
                'observacoes'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar')
            )
        )

    class Meta:
        """
        Meta class for defining metadata options for the Coleta_lagoa form.
        """
        model = Coleta_lagoa
        fields = ['data_coleta', 'local_coleta', 'responsavel_coleta', 'pH', 'temperatura', 'turbidez', 'oxigenio_dissolvido',
                  'observacoes']
        widgets = {
            'data_coleta': forms.DateInput(attrs={'type': 'date', 'class': 'flatpickr'}),
        }
    
