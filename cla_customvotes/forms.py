
from django import forms
from django.core.exceptions import ValidationError
from .models import Candidate


class CustomVoteForm(forms.Form):

    vote1 = forms.ChoiceField(
        label="Je vote pour",
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


class CustomVoteProxyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.candidates = kwargs.pop('candidates')
        self.proxy = kwargs.pop('proxy')
        super().__init__(*args, **kwargs)

        self.mapping = {}
        for candidate in self.candidates:
            self.mapping[candidate.pk] = f"vote_{candidate.pk}"
            self.fields[f"vote_{candidate.pk}"] = forms.IntegerField(label=str(candidate), min_value=0)

        self.mapping[-1] = 'vote_blank'
        self.fields['vote_blank'] = forms.IntegerField(label="Votes blancs", min_value=0)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"

    def clean_vote_blank(self):
        total = 0
        for name, value in self.cleaned_data.items():
            print(name, value)
            total += value
        print(total)
        if total != self.proxy.total:
            raise ValidationError(f"Vous devez répartir correctement vos {self.proxy.total} votes.")
        return self.cleaned_data['vote_blank']

    def get_vote_for(self, candidate: Candidate):
        return self.cleaned_data[self.mapping[candidate.pk]]
