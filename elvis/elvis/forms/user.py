from django import forms

class UserForm(forms.Form):
	first_name = forms.CharField(max_length=255)
	last_name = forms.CharField(max_length=255)
	# Username can't already be taken 
	username = forms.CharField()
	# Password must be strong enough
	password = forms.CharField()
	# Email can't already be in use 
	email = forms.EmailField()

	picture = forms.ImageField(required=False)


'''
Used to invite user to website, project
'''
class InviteUserForm(forms.Form):
	email = forms.EmailField()
	subject = forms.CharField(max_length=255)
	message = forms.CharField(widget=forms.Textarea)