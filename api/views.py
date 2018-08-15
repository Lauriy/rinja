# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import generics

from api.serializers import CaptchaSerializer


class CaptchaCreate(generics.CreateAPIView):
    serializer_class = CaptchaSerializer