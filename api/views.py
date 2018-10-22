# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bs4
import requests
from django.core.files.base import ContentFile
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.models import Captcha, Stock
from api.serializers import CaptchaSerializer, GuessCaptchaSerializer


class RetrieveCaptcha(generics.RetrieveAPIView):
    serializer_class = CaptchaSerializer
    captcha_image_url_template = 'https://nasdaqcsd.com/statistics//graphics/captcha/%s.png'

    def retrieve(self, request, *args, **kwargs):
        captcha_page = requests.get('https://nasdaqcsd.com/statistics/en/shareholders')
        session_id = captcha_page.cookies['PHPSESSID']
        soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
        captcha_id = soup.select('#captcha-id')[0]['value']
        captcha_image_url = self.captcha_image_url_template % captcha_id
        image_content = ContentFile(requests.get(captcha_image_url).content)
        instance = Captcha(
            md5=captcha_id,
            session_id=session_id,
            created_by=request.user
        )
        instance.save()
        instance.image.save(captcha_id + '.png', image_content, False)
        instance.save()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)


class GuessCaptcha(generics.RetrieveUpdateAPIView):
    # queryset = Captcha.objects.filter(answer__isnull=True)
    queryset = Captcha.objects.all()
    serializer_class = GuessCaptchaSerializer
    captcha_validation_url_template = \
        'https://nasdaqcsd.com/statistics/en/shareholders?security=%s&captcha[id]=%s&captcha[input]=%s'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Get random stock to try the captcha answer on
        # TODO: Get one that hasn't been updated today first
        stock = Stock.objects.order_by('?').first()
        validation_url = self.captcha_validation_url_template % (stock.isin, instance.md5,
                                                                 serializer.validated_data['answer'])
        validation_page = requests.get(validation_url, cookies=dict(PHPSESSID=instance.session_id))
        soup = bs4.BeautifulSoup(validation_page.text, 'html.parser')
        try:
            shareholders_table = soup.select('.most-numbers')[0]
            print (shareholders_table)
            self.perform_update(serializer)
        except:
            raise ValidationError('Failed to validate CAPTCHA answer', 400)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ListCaptcha(generics.ListAPIView):
    queryset = Captcha.objects.all()
    serializer_class = CaptchaSerializer
