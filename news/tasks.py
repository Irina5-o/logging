import logging

from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from .models import Post, Category


logger = logging.getLogger(__name__)

@shared_task
def send_weekly_newsletters():
    """
    Еженедельная рассылка новостей подписчикам
    Выполняется каждый понедельник в 8 утра
    """
    logger.info("Запуск еженедельной рассылки новостей")
    end_date = timezone.now()
    start_date = end_date - timedelta(weeks=1)

    # Собираем всех пользователей с подписками
    users_with_subs = User.objects.filter(subscribed_categories__isnull=False).distinct()

    for user in users_with_subs:
        if not user.email:
            continue

        # Проверяем подтвержденный email
        if not EmailAddress.objects.filter(user=user, email=user.email, verified=True).exists():
            continue

        # Получаем все категории пользователя
        user_categories = user.subscribed_categories.all()

        # Собираем все новости за неделю в подписанных категориях
        news = Post.objects.filter(
            categories__in=user_categories,
            post_type=Post.NEWS,
            created_at__range=[start_date, end_date]
        ).distinct().order_by('-created_at')

        if not news.exists():
            logger.info(f"Нет новых новостей для пользователя {user.email}")
            continue

        try:
            # Формируем HTML-содержимое
            html_content = render_to_string(
                'weekly_newsletter.html',
                {
                    'user': user,
                    'posts': news,
                    'site_url': settings.SITE_DOMAIN
                }
            )

            subject = 'Еженедельная подборка новостей'
            msg = EmailMultiAlternatives(
                subject=subject,
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info(f"Еженедельная рассылка отправлена на {user.email}")
        except Exception as e:
            logger.error(f"Ошибка отправки новостей для {user.email}: {e}")

@shared_task
def send_article_notifications(post_id):
    """
    Отправляет уведомления подписчикам о новой статье
    """
    try:
        post = Post.objects.get(id=post_id, post_type=Post.ARTICLE)
        logger.info(f"Обработка уведомлений для статьи: {post.title} (ID: {post.pk})")

        # Собираем всех подписчиков категорий статьи
        subscribers = set()
        for category in post.categories.all().prefetch_related('subscribers'):
            subscribers.update(category.subscribers.all())

        logger.info(f"Всего подписчиков для уведомления: {len(subscribers)}")

        for user in subscribers:
            if not user.email:
                continue

            # Проверяем подтвержденный email
            if not EmailAddress.objects.filter(user=user, email=user.email, verified=True).exists():
                continue

            # Категории статьи, на которые подписан пользователь
            user_categories = [cat for cat in post.categories.all() if user in cat.subscribers.all()]
            if not user_categories:
                continue

            try:
                subject = f'Новая статья в категориях: {", ".join(c.name for c in user_categories)}'

                html_content = render_to_string(
                    'article_notification.html',
                    {
                        'user': user,
                        'post': post,
                        'categories': user_categories,
                        'site': settings.SITE_DOMAIN
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info(f"Уведомление о статье отправлено на {user.email}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления для {user.email}: {e}")

    except Post.DoesNotExist:
        logger.error(f"Статья с id {post_id} не найдена")
    except Exception as e:
        logger.error(f"Ошибка в задаче send_article_notifications: {str(e)}")
        raise