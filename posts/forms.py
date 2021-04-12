from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': 'Сообщество',
            'text': 'Текст записи',
        }
        help_texts = {
            'group': 'Выберите сообщество',
            'text': 'Введите о чем хотите написать',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
