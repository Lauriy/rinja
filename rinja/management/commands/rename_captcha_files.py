import os

from django.core.management.base import BaseCommand

from rinja.models import Captcha


class Command(BaseCommand):
    help = 'Renames all the captured CAPTCHA image files to {answer}.png'

    def handle(self, *args, **options):
        captchas = Captcha.objects.all()
        for captcha in captchas:
            path_parts = captcha.image.path.split('/')
            new_path = '/'.join(path_parts[:-1]) + '/' + captcha.answer + '.png'
            new_name = '/'.join(new_path.split('/')[4:])
            os.rename(captcha.image.path, new_path)
            captcha.image.name = new_name
            captcha.save()
