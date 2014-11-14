from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):

    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=True)
    picture = forms.ImageField(required=False)

    class Meta:
        model = User 
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.picture = self.cleaned_data['picture']

        if commit:
            user.save()

        return User.objects.get(pk=user.id)

'''
Used to invite user to website, project
'''
class InviteUserForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)