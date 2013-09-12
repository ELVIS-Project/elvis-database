from django import forms

class ComposerForm(forms.Form):
    name = forms.CharField(max_length=255)
    birth_date = forms.CharField(required=False)
    death_date = forms.CharField(required=False)
    picture = forms.ImageField(required=False)

    def validate_date(self, birth, death): return birth < death 

class CorpusForm(forms.Form):
	title = forms.CharField(max_length=255)
	comment = forms.CharField(widget=forms.Textarea, required=False)
	picture = forms.ImageField(required=False)

class PieceForm(forms.Form):
    title = forms.CharField(max_length=255)
    composer = forms.CharField(max_length=255)
    corpus = forms.CharField(max_length=255)
    date_of_composition = forms.CharField(required=False)
    number_of_voices = forms.IntegerField(required=False)
    tags = forms.CharField(widget=forms.Textarea)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    attachment = forms.FileField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

class AttachmentForm(forms.Form):
	title = forms.CharField(max_length=255)
	description = forms.CharField(widget=forms.Textarea, required=False)

class MovementForm(forms.Form):
    title = forms.CharField(max_length=255)
    piece = forms.CharField(max_length=255)
    attachment = forms.FileField()
    composer = forms.CharField(max_length=255)
    corpus = forms.CharField(max_length=255)
    date_of_composition = forms.CharField(required=False)
    number_of_voices = forms.IntegerField(required=False)
    tags = forms.CharField(widget=forms.Textarea)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    description = forms.CharField(max_length=255, required=False)



