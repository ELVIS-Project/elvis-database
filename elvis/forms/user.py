from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from elvis.models.user_profile import UserProfile


# A simple extension of the built-in UserCreationForm
class ElvisUserCreationForm(UserCreationForm):

    # Gather data
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=True)
    picture = forms.ImageField(required=False)

    # Define available fields from the form for the user
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('Account with that email already exists')
        return email

    # Clean data, create the user using UserCreationForm, return the new user obj for login
    def save(self, commit=True):
        user = self.instance
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.picture = self.cleaned_data['picture']

        if commit:
            user.save()
            try:
                user_profile = UserProfile(user=user)
                user_profile.save()
            except:
                user.delete()
                raise

        return user


class ElvisUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and any(x != self.instance for x in User.objects.filter(email=email)):
            raise forms.ValidationError('Account with that email already exists')
        return email

    def clean_password(self):
        pass

    def save(self, commit=True):
        user = self.instance
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()


class InviteUserForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
