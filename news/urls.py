from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (
    NewsList, NewsDetail, NewsSearch,
    NewsCreate, NewsUpdate, NewsDelete, SubscriptionsView
)

urlpatterns = [
    path('', cache_page(60)(NewsList.as_view()), name='news_list'),
    path('<int:pk>/', cache_page(300)(NewsDetail.as_view()), name='news_detail'),
    path('search/', NewsSearch.as_view(), name='news_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('articles/create/', NewsCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', NewsUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', NewsDelete.as_view(), name='article_delete'),
    # Подписки
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
]