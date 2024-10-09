from django import forms


class SubirArchivoForm(forms.Form):
    archivo = forms.FileField(label='Sube tu archivo Excel', widget=forms.ClearableFileInput(attrs={'multiple': False}))