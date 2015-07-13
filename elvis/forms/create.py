from django import forms

class PieceForm(forms.Form):
    # Basic Fields
    title = forms.CharField()
    composer = forms.CharField()
    composition_start_date = forms.DateField(required=False)
    composition_end_date = forms.DateField(required=False)

    # New composer fields
    composer_birth_date = forms.DateField(required=False)
    composer_death_date = forms.DateField(required=False)

    collections = forms.CharField(required=True)
    number_of_voices = forms.IntegerField(required=True)
    genres = forms.CharField(required=True)
    locations = forms.CharField(required=False)
    sources = forms.CharField(required=False)
    instruments_voices = forms.CharField(required=True)
    comment = forms.CharField(required=False)
    religiosity = forms.CharField(required=True)
    vocalization = forms.CharField(required=True)
    tags = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(PieceForm, self).clean()
        if cleaned_data['composition_start_date'] and not cleaned_data['composition_end_date']:
            cleaned_data['composition_end_date'] = cleaned_data['composition_start_date']
            return cleaned_data

        if not cleaned_data['composition_start_date'] and not cleaned_data['composition_end_date']:
            self.add_error("composition_end_date", forms.ValidationError("At least one date required."))

        if (cleaned_data['vocalization'] == "Vocal" or cleaned_data['vocalization'] == "Mixed") and not cleaned_data['languages']:
            self.add_error("languages", forms.ValidationError("Language is required for vocal/mixed pieces."))


class CollectionForm(forms.Form):
    title = forms.CharField()
    permission = forms.CharField(required=False)
    comment = forms.CharField(required=False)
