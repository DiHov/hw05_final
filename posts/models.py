from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Имя группы',
        help_text='Дайте имя группе',
        max_length=200
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка для группы',
        help_text='Задайте ссылку',
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Опишите сообщество'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текс нового поста',
        help_text='Введите текст своей записи'
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
        help_text='Авторство присваивается автоматически'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа поста',
        help_text='Выберите группу для поста'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемая запись',
        help_text='Прокомментируйте запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Авторство присваивается автоматически'
    )
    text = models.TextField(
        verbose_name='Текс комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        'date created',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:10]
