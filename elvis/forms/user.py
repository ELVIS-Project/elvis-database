from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# A simple extension of the built-in UserCreationForm
class UserForm(UserCreationForm):

    # Gather data
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=True)
    picture = forms.ImageField(required=False)

    # Define available fields from the form for the user
    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2']

    # Clean data, create the user using UserCreationForm, return the new user obj for login
    def save(self, commit=True):
        user = super(UserForm, self).save(commit = False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.picture = self.cleaned_data['picture']

        if commit:
            user.save()

        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    username = forms.CharField(required=False)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=False)



class InviteUserForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
