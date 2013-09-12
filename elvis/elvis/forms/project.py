from django import forms

class ProjectForm(forms.Form):
	name = forms.CharField(max_length=255)
	description = forms.CharField(widget=forms.Textarea, required=False)
	users = forms.CharField(widget=forms.Textarea, required=False)

class DiscussionForm(forms.Form):
	name = forms.CharField(max_length=255)
	comment = forms.CharField(widget=forms.Textarea)
	#project = foreign key
	#user = current user

class CommentForm(forms.Form):
	name = forms.CharField(max_length=255, required=False)
	text = forms.CharField(widget=forms.Textarea)
    #user = current user
    #discussion = current discussion

class TodoForm(forms.Form):
	name = forms.CharField(max_length=255, required=False)
	description = forms.CharField(widget=forms.Textarea)
	due_date = forms.DateField(required=False)
	#project = current project
	#assigned_to = foreign key user -- need some kind of interaction with notification form? 
