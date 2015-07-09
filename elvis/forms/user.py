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

# Custom updating form
class UserUpdateForm(forms.ModelForm):

    # Gather data
    username = forms.CharField(required=False)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=False)
    picture = forms.ImageField(required=False)
    update_password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=True)


    class Meta:
        model = User 
        fields = '__all__'

    # Fill any blanks user left by looking at instance
    def fill_blanks(self):
        f_username = self.username if self.username else self.instance.username
        f_email = self.email if self.email else self.instance.email
        f_first_name = self.first_name if self.first_name else self.instance.first_name
        f_last_name = self.last_name if self.last_name else self.instance.last_name
        f_picture = self.picture if self.picture else self.instance.picture
        f_password = self.password if self.password else self.instance.password

    def clean(self):
        self.fill_blanks()
        super(UserUpdateForm, self).clean()
        self.clean_password2()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit = False)
        user.username = self.cleaned_data['username'] if self.cleaned_data['username'] != '' else self.instance.username
        user.email = self.cleaned_data['email'] if self.cleaned_data['email'] != '' else self.instance.email
        user.first_name = self.cleaned_data['first_name'] if self.cleaned_data['first_name'] != '' else self.instance.first_name
        user.last_name = self.cleaned_data['last_name'] if self.cleaned_data['last_name'] != '' else self.instance.last_name
        user.picture = self.cleaned_data['picture'] if self.cleaned_data['picture'] != '' else self.instance.picture
        user.password = self.clean_password2() if self.cleaned_data['password1'] != '' else self.instance.password

        if commit:
            user.save()

        return user

class InviteUserForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
