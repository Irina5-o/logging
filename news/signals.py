import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import send_article_notifications

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if not created or instance.post_type != Post.ARTICLE:
        return

    logger.info(f"Запуск задачи уведомления для статьи ID: {instance.pk}")
    send_article_notifications.delay(instance.id)