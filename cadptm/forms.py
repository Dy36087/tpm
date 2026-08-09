from django import forms
from .models import Patrimonio


class PatrimonioForm(forms.ModelForm):
    status = forms.ChoiceField(
        label="Status",
        choices=Patrimonio.STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-radio"}),
    )

    estado_conservacao = forms.ChoiceField(
        label="Estado de Conservação",
        choices=Patrimonio.ESTADO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    tipo = forms.ChoiceField(
        label="Tipo",
        choices=Patrimonio.TIPO,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    
    destino = forms.ChoiceField(
        label="Destino",
        choices=Patrimonio.DESTINO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Patrimonio
        fields = [
            "tipo",
            "codigo",
            "material",
            "destino",
            "estado_conservacao",
            "quantidade",
            "valor",
            "data_aquisicao",
            "localizacao",
            "status",
        ]
        widgets = {
            "tipo": forms.TextInput(attrs={"class": "form-control"}),
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "material": forms.TextInput(attrs={"class": "form-control"}),
            "destino": forms.TextInput(attrs={"class": "form-control"}),
            "quantidade": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.TextInput(attrs={"class": "form-control"}),
            "data_aquisicao": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "localizacao": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "tipo": "Tipo",
            "codigo": "Código Unico Equipamento",
            "material": "Material",
            "destino": "Destino",
            "estado_conservacao": "Estado de Conservação",
            "quantidade": "Quantidade",
            "valor": "Valor",
            "data_aquisicao": "Data de Aquisição",
            "localizacao": "Localização",
            "status": "Status",
        }
