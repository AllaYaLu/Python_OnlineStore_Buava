from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загружает товары и остатки из файла JSON в базу данных'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Запуск импорта данных...'))
        try:
            # Вызываем встроенную команду loaddata для файла data.json
            call_command('loaddata', 'data.json')
            self.stdout.write(self.style.SUCCESS('Данные успешно загружены из data.json!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при импорте: {e}'))
            self.stdout.write(self.style.WARNING('Подсказка: Убедитесь, что файл data.json создан в корне проекта.'))
