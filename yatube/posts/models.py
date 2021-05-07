from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              verbose_name='Группа',
                              help_text='Дайте короткое название группы',
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.author} | {self.text[:15]}'

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()            
    created = models.DateTimeField('Дата комментария', 
                                   auto_now_add=True)

    def __str__(self):
        return f'{self.author} | {self.text[:15]}'

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following")