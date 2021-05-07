from .models import Post, Comment
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
            'image': _('Изображение'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': _('Текст комментария'),
        }
