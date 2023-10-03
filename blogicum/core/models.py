from django.db import models


class PublishedDateModel(models.Model):
    """Абстрактная модель. Добавляет флаги is_published и created_at."""
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
