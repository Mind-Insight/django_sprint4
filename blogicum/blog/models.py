from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import truncatechars

from blog.abstracts import TimeStampedModel


User = get_user_model()


class Post(TimeStampedModel):
    title = models.CharField(
        "Заголовок",
        max_length=256,
        blank=False,
    )
    text = models.TextField("Текст", blank=False)
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        blank=False,
        help_text=(
            "Если установить дату и время в "
            "будущем — можно делать отложенные публикации."
        ),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор публикации",
        related_name="posts",
    )

    location = models.ForeignKey(
        "Location",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Местоположение",
        related_name="posts",
    )

    category = models.ForeignKey(
        "Category",
        null=True,
        on_delete=models.SET_NULL,
        blank=False,
        verbose_name="Категория",
        related_name="posts",
    )

    image = models.ImageField(
        "Картинка",
        upload_to="media/",
        blank=True,
    )

    @property
    def short_text(self):
        return truncatechars(self.text, 100)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title


class Category(TimeStampedModel):
    title = models.CharField(
        "Заголовок",
        max_length=256,
        blank=False,
    )
    description = models.TextField(
        "Описание",
        blank=False,
    )
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        blank=False,
        help_text=(
            "Идентификатор страницы для URL; разрешены "
            "символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(TimeStampedModel):
    name = models.CharField(
        "Название места",
        max_length=256,
        blank=False,
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(
        "Текст комментария",
        max_length=500,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.text
