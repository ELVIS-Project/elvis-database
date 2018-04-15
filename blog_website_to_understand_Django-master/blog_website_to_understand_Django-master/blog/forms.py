from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('author', 'title', 'text',)  # who posted it, the title and the text
        # By using these attributes, the author, title and text defined in Post, will automatically produce a form, when
        #form.as_p is required
        # the line above inherits from the model Post and present it as a form, and we want author, title and text to be
        # in the form

        widgets = {
            'title': forms.TextInput(attrs={'class': 'textinputclass'}), # 'textinputclass' this is css class
            'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'}) # it contains 3 css classes

        }  # however, we can comment widgets area, and the form can still be displayed (maybe not as pretty as using CSS)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields =('author', 'text')

        widgets = {
            'author': forms.TextInput(attrs={'class': 'textinputclass'}),  # widget connects css file
            'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})
        }