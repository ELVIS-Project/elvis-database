from django import forms


class PieceForm(forms.Form):
    """Validate piece upload form.

     This form can only validate the static fields (i.e. check that
     required fields are there). For this reason, when this form is used
     in views/piece, it is first passed to validate_dynamic_piece_form().
    """
    # Basic Fields
    title = forms.CharField()
    composer = forms.CharField()
    composition_start_date = forms.IntegerField(required=False)
    composition_end_date = forms.IntegerField(required=False)

    # New composer fields
    composer_birth_date = forms.IntegerField(required=False)
    composer_death_date = forms.IntegerField(required=False)

    collections = forms.CharField(required=True)
    number_of_voices = forms.IntegerField(required=True)
    genres = forms.CharField(required=True)
    locations = forms.CharField(required=False)
    languages = forms.CharField(required=False)
    sources = forms.CharField(required=False)
    instruments_voices = forms.CharField(required=True)
    comment = forms.CharField(required=False)
    religiosity = forms.CharField(required=True)
    vocalization = forms.CharField(required=True)
    tags = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(PieceForm, self).clean()
        if cleaned_data.get('composition_start_date') and not cleaned_data.get('composition_end_date'):
            cleaned_data['composition_end_date'] = cleaned_data['composition_start_date']
            return cleaned_data

        if not cleaned_data.get('composition_start_date') and not cleaned_data.get('composition_end_date'):
            self.add_error("composition_end_date", forms.ValidationError("At least one date required."))

        if (cleaned_data.get('vocalization') == "Vocal" or cleaned_data.get('vocalization') == "Mixed") and not cleaned_data.get('languages'):
            self.add_error("languages", forms.ValidationError("Language is required for vocal/mixed pieces."))


def validate_dynamic_piece_form(request, form):
    """Validate the dynamic and static fields on the piece create form.
    :param request: The relevant django request object.
    :param form: a PieceForm
    :return: a validated PieceForm.
    """
    form.is_valid()
    movement_title_list = [x for x in list(request.POST.keys()) if x.startswith('_existingmov_title_')]
    for mov in movement_title_list:
        if not request.POST.get(mov):
            form.add_error(None, [mov, "Movements require a title."])

    file_source_list = [x for x in list(request.POST.keys()) if x.startswith('files_source')]
    for source in file_source_list:
        if request.FILES.get(source.replace('source', 'files')) and not request.POST.get(source):
            form.add_error(None, [source, "Files require a source!<br>"])

    return form


class CollectionForm(forms.Form):
    """Validates a new collection form."""
    title = forms.CharField()
    permission = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    initialize_empty = forms.BooleanField(required=False)
