
from django import forms


class BdxVoteForm(forms.Form):

    vote = forms.ChoiceField(
        label="Je vote pour",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign')
        super().__init__(*args, **kwargs)
        choices = [(0, 'Aucune liste (vote blanc)')]
        for list in campaign.lists.all():
            choices.append((list.pk, f"La liste {list.name}"))
        self.fields['vote'].choices = choices
