
from django import forms


class EnsclLoginForm(forms.Form):
    email = forms.EmailField(
        label='Adresse mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'prenom.nom@enscl.centralelille.fr'})
    )


class EnsclCodeForm(forms.Form):
    code = forms.CharField(
        label='Code reçu par mail',
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class EnsclVoteForm(forms.Form):

    pole_eleve = forms.ChoiceField(
        label="Pôle élève : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pole_foyer = forms.ChoiceField(
        label="Pôle foyer : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pole_sport = forms.ChoiceField(
        label="Pôle sport : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pole_art = forms.ChoiceField(
        label="Pôle art : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pole_dd = forms.ChoiceField(
        label="Pôle développement durable : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pole_cpi = forms.ChoiceField(
        label="Pôle CPI : je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pole_eleve'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('La Monarchimie', 'La Monarchimie'),
            ('Disc’O2', 'Disc’O2')
        ]

        self.fields['pole_foyer'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('Galadiators', 'Galadiators')
        ]

        self.fields['pole_sport'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('The Hunger Olympic Games', 'The Hunger Olympic Games')
        ]

        self.fields['pole_art'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('Laborato’art', 'Laborato’art')
        ]

        self.fields['pole_dd'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('orchi-DD', 'orchi-DD')
        ]

        self.fields['pole_cpi'].choices = [
            ('Vote blanc', 'Aucune liste (vote blanc)'),
            ('Magazinc', 'Magazinc')
        ]

