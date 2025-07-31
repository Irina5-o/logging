from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаление постов из категорий'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        category_name = options["category"]
        answer = input(f'Вы правда хотите удалить все статьи в категории "{category_name}"? yes/no: ')

        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Отменено'))
            return

        try:
            category = Category.objects.get(name=category_name)
            Post.objects.filter(categories=category).delete()
            self.stdout.write(self.style.SUCCESS(
                f'Успешно удалены все посты из категории {category.name}'
            ))
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Не удалось найти категорию '{category_name}'"
            ))