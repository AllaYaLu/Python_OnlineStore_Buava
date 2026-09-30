import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Экспортирует остатки товаров со склада в файл JSON'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Запуск экспорта остатков...'))
        try:
            # Нужно выгрузить только модель Stock из приложения store
            with open('residue.json', 'w', encoding='utf-8') as f:
                call_command('dumpdata', 'store.Stock', stdout=f, indent=4)
                
            self.stdout.write(self.style.SUCCESS('Остатки успешно выгружены в файл residue.json!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при экспорте: {e}'))
