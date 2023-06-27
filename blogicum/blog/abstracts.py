from django.db import models


class TimeStampedModel(models.Model):
    """Абстрактная модель добавляет дату создания и флаг is_published"""

    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        blank=False,
        help_text="""Снимите галочку, чтобы скрыть публикацию.""",
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
        blank=False,
    )

    class Meta:
        abstract = True
