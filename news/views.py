from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView
)
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm


class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_count'] = Post.objects.count()
        context['filterset'] = self.filterset
        return context

class NewsSearch(ListView):
    model = Post
    ordering = "-created_at"
    template_name = "search.html"
    context_object_name = "news"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_item'

    def get_object(self, queryset=None):
        news_id = self.kwargs.get('pk')
        cache_key = f'post-{news_id}'
        obj = cache.get(cache_key)
        if obj is None:
            obj = super().get_object(queryset=queryset)
            cache.set(cache_key, obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context


class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = "post_edit.html"
    success_url = reverse_lazy('news_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, состоит ли пользователь в группе "author"
        if not request.user.groups.filter(name="author").exists():
            messages.error(request, "У вас недостаточно прав для создания поста.")
            return redirect('news_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        # Назначаем тип поста в зависимости от URL
        if "articles" in self.request.path:
            post.post_type = Post.ARTICLE
        else:
            post.post_type = Post.NEWS

        # Присваиваем автора, используя связанный профиль Author
        # Для каждого пользователя из группы "author" должен быть создан объект Author
        try:
            post.author = self.request.user.author
        except Exception:
            messages.error(self.request, "Ваш профиль автора не найден. Обратитесь к администратору.")
            return redirect('news_list')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "articles" in self.request.path:
            context["get_title"] = "Создать статью"
            context["get_header"] = "Добавить статью"
        else:
            context["get_title"] = "Создать новость"
            context["get_header"] = "Добавить новость"
        return context


class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = "post_edit.html"
    success_url = reverse_lazy('news_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.post_type == Post.ARTICLE:
            context["get_title"] = "Редактировать статью"
            context["get_header"] = "Редактирование статьи"
        else:
            context["get_title"] = "Редактировать новость"
            context["get_header"] = "Редактирование новости"
        return context


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')


class SubscriptionsView(LoginRequiredMixin, TemplateView):
    """Представление для управления подписками"""
    template_name = 'subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Используем related_name 'subscribed_categories'
        context['user_subscriptions'] = self.request.user.subscribed_categories.all()
        return context

    def post(self, request, *args, **kwargs):
        """Обработка формы подписок"""
        user = request.user
        category_ids = request.POST.getlist('categories')
        user.subscribed_categories.set(category_ids)

        messages.success(
            request,
            "Ваши подписки успешно обновлены!"
        )

        return redirect('subscriptions')

# Тестовое представление для проверки email
#def test_email_view(request):
#    """Временное представление для тестирования email"""
#    try:
#        send_mail(
#            'Test Subject',
#            'Test message body',
#            settings.DEFAULT_FROM_EMAIL,
#            ['your_test_email@gmail.com'],
#            fail_silently=False,
#        )
#        return HttpResponse("Тестовое письмо отправлено!")
#    except Exception as e:
#        return HttpResponse(f"Ошибка отправки: {str(e)}")