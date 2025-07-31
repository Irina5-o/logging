from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Расчет рейтинга на основе постов, комментариев и комментариев к постам автора
        post_rating = sum(post.rating * 3 for post in self.post_set.all())
        comment_rating = sum(comment.rating for comment in Comment.objects.filter(author=self.user))
        post_comments_rating = sum(comment.rating for comment in Comment.objects.filter(post__author=self))

        self.rating = post_rating + comment_rating + post_comments_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(
        User,
        related_name='subscribed_categories',
        blank=True
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'

    POST_TYPE_CHOICES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='post_set')
    post_type = models.CharField(max_length=2, choices=POST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.text[:124]}..." if len(self.text) > 124 else self.text

    def __str__(self):
        return f"{self.title.title()}: {self.text[:20]}"

    def get_absolute_url(self):
        return reverse("news_detail", args=[str(self.id)])

    def clean(self):
        # Определяем лимиты для разных типов публикаций
        limits = {
            self.NEWS: 3,  # Не более 3 новостей в день
            self.ARTICLE: 5  # Не более 5 статей в день
        }

        # Проверяем, есть ли ограничение для текущего типа публикации
        if self.post_type in limits:
            today = timezone.now().date()
            limit = limits[self.post_type]

            # Получаем количество публикаций этого типа за сегодня
            posts_today = Post.objects.filter(
                author=self.author,
                post_type=self.post_type,
                created_at__date=today
            ).exclude(id=self.id).count()

            # Проверяем превышение лимита
            if posts_today >= limit:
                type_name = dict(self.POST_TYPE_CHOICES)[self.post_type].lower()
                raise ValidationError(
                    f"Нельзя создавать более {limit} {type_name} в день! "
                    f"Вы уже создали {posts_today} {type_name} сегодня."
                )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала сохраняем в базе
        cache.delete(f'post-{self.pk}')  # затем удаляем соответствующий ключ из кэша


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"{self.author.username}: {self.text[:30]}"