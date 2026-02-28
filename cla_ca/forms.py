
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

    blank_vote = forms.BooleanField(
        label="Je vote blanc (ne classer aucun candidat)",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'blank_vote_checkbox'})
    )

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
                widget=forms.Select(attrs={'class': 'form-control rank-field'}),
            )

        self._ranked_candidates = []

    def clean(self):
        cleaned = super().clean()
        blank_vote = cleaned.get('blank_vote', False)
        used_ranks = {}
        ranked_count = 0

        for candidate in self.candidates:
            field_name = f"rank_{candidate.pk}"
            value = cleaned.get(field_name)
            if not value:
                continue

            ranked_count += 1

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

        # Validation : soit vote blanc sans classement, soit tous les candidats classés
        if blank_vote and ranked_count > 0:
            self.add_error('blank_vote', "Vous ne pouvez pas voter blanc et classer des candidats en même temps.")
        elif not blank_vote and ranked_count > 0 and ranked_count < len(self.candidates):
            raise forms.ValidationError(
                f"Vous devez classer tous les candidats ({len(self.candidates)}) ou voter blanc. "
                f"Vous avez classé {ranked_count} candidat(s)."
            )
        elif not blank_vote and ranked_count == 0:
            raise forms.ValidationError(
                "Vous devez soit classer tous les candidats, soit cocher la case \"Vote blanc\"."
            )

        self._ranked_candidates = [
            used_ranks[rank] for rank in sorted(used_ranks.keys())
        ]
        return cleaned

    def get_ranked_candidates(self):
        return self._ranked_candidates
