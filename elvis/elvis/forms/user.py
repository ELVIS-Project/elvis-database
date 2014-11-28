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


    class Meta:
        model = User 
        fields = '__all__'
        #fields = ['username', 'email', 'password1', 'password2']

    # Fill any blanks user left by looking at instance
    def fill_blanks(self):
        self.username = self.username if self.username else self.instance.username
        self.email = self.email if self.email  else self.instance.email
        self.first_name = self.first_name  if self.first_name else self.instance.first_name
        self.last_name = self.last_name if self.last_name else self.instance.last_name
        self.picture = self.picture if self.picture  else self.instance.picture
        self.password = self.password if self.password else self.instance.password

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


    '''
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=True)
    picture = forms.ImageField(required=False)

    # Define available fields from the form for the user
    class Meta:
        model = User 
        fields = '__all__'

    # Clean data.
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email

    # Update user. The user object is not necessary, but for typing purposes
    # we'll return it anyway
    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit = False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.picture = self.cleaned_data['picture']
        user.password = self.clean_password2()

        if commit:
            user.save()

        return User.objects.get(pk=user.id)
    '''

'''
Used to invite user to website, project
'''
class InviteUserForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
