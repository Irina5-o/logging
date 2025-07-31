from django.contrib import admin
from .models import Post, Category, Comment, Author, PostCategory

class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'author', 'rating')
    list_filter = ('created_at', 'author', 'categories')
    search_fields = ('title', 'text')
    inlines = [PostCategoryInline]

class CategoryAdmin(admin.ModelAdmin):
    filter_horizontal = ('subscribers',)  # Добавлено для удобства управления подписками

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Author)
