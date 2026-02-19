
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


class CaCondorcetVoteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        candidates = list(kwargs.pop('candidates'))
        super().__init__(*args, **kwargs)
        self.candidates = candidates

        rank_choices = [('', 'Non classé')]
        for index in range(1, len(candidates) + 1):
            rank_choices.append((str(index), str(index)))

        for candidate in candidates:
            self.fields[f"rank_{candidate.pk}"] = forms.ChoiceField(
                label=f"Classement - {candidate.first_name} {candidate.last_name}",
                required=False,
                choices=rank_choices,
                widget=forms.Select(attrs={'class': 'form-control'}),
            )

        self._ranked_candidates = []

    def clean(self):
        cleaned = super().clean()
        used_ranks = {}

        for candidate in self.candidates:
            field_name = f"rank_{candidate.pk}"
            value = cleaned.get(field_name)
            if not value:
                continue

            try:
                rank = int(value)
            except (TypeError, ValueError):
                self.add_error(field_name, "Classement invalide.")
                continue

            if rank < 1 or rank > len(self.candidates):
                self.add_error(field_name, "Classement invalide.")
                continue

            if rank in used_ranks:
                self.add_error(field_name, "Ce rang est déjà utilisé.")
                continue

            used_ranks[rank] = candidate.pk

        self._ranked_candidates = [
            used_ranks[rank] for rank in sorted(used_ranks.keys())
        ]
        return cleaned

    def get_ranked_candidates(self):
        return self._ranked_candidates
