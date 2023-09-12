from ckeditor import widgets
from django import forms

from app.models import Post, Category


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'categories', 'content', 'hashtags', 'mode')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title (*)'}),
            'categories': forms.SelectMultiple(),
            'content': forms.CharField(widget=widgets.CKEditorWidget()),
            'mode': forms.Select(attrs={'class': 'btn btn-default border border-gray'}),
        }
        # not required hashtags field
        required = {'hashtags': False}
