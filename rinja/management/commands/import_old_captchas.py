import os
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from rinja.models import Captcha


class Command(BaseCommand):
    help = 'Import historical \'hand-solved\' CAPTCHAS'

    def handle(self, *args, **options):
        files = os.listdir('import')
        for file in files:
            image = Image.open('import/' + file)
            print(file)
            answer = file[:4]
            f = BytesIO()
            image.save(f, format='png')
            captcha = Captcha(answer=answer)
            captcha.image.save(answer + '.png', ContentFile(f.getvalue()))
            f.close()
