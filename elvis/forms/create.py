from django import forms


class PieceForm(forms.Form):
    # Basic Fields
    title = forms.CharField()
    composer = forms.CharField()

    # New composer fields
    is_new_composer = forms.CharField()
    composer_birth_date = forms.DateField(required=False)
    composer_death_date = forms.DateField(required=False)

    collection = forms.CharField(required=False)
    comp_start = forms.CharField(required=False)
    comp_end = forms.CharField(required=False)
    number_of_voices = forms.IntegerField(required=False)
    # Additional Fields
    genre = forms.CharField(required=False)
    voices = forms.CharField(required=False)
    composer_country = forms.CharField(required=False)
    language = forms.CharField(required=False)
    source = forms.CharField(required=False)
    # Tags - will probably be complicated.
    tags = forms.CharField(required=False)
    # Comment
    comment = forms.CharField(required=False)

    # Movements
    movements = forms.CharField(required=False)