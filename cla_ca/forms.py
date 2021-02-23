
from django import forms


class CaVoteForm(forms.Form):

    vote1 = forms.ChoiceField(
        label="Je donne mon premier vote à",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    vote2 = forms.ChoiceField(
        label="Je donne mon second vote à",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        candidates = kwargs.pop('candidates')
        super().__init__(*args, **kwargs)
        choices = [(0, 'Aucun candidat (vote blanc)')]
        for candidate in candidates:
            choices.append((candidate.pk, f"{candidate.first_name} {candidate.last_name}"))
        self.fields['vote1'].choices = choices
        self.fields['vote2'].choices = choices
