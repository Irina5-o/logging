from django import forms
from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from .models import Post, Author

class PostFilter(FilterSet):
    title = CharFilter(
            label='Содержит',
            lookup_expr='icontains'
    )
    author = ModelChoiceFilter(
            queryset=Author.objects.all(),
            lookup_expr='exact',
            label='Автор',
            empty_label='Все авторы'
    )
    date_published = DateFilter(
            field_name='created_at',
            label='Опубликованы после',
            lookup_expr='gt',
            widget=forms.DateInput(attrs={'type': 'date', 'class': 'form'})
    )

    class Meta:
        model = Post
        fields = []