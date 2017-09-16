import urllib

import bs4
import requests
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, TemplateView

from forms import CaptchaAddForm
from rinja.models import Captcha


class HomeView(TemplateView):
    template_name = 'home.html'


class CaptchaCreate(CreateView):
    model = Captcha
    form_class = CaptchaAddForm
    success_url = reverse_lazy('captcha_add')
    captcha_image_url_template = 'http://statistics.e-register.ee/graphics/captcha/%s.png'

    def get(self, request, *args, **kwargs):
        self.object = None
        ctx = self.get_context_data()
        captcha_page = requests.get('http://statistics.e-register.ee/et/shareholders')
        soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
        captcha_id = soup.select('#captcha-id')[0]['value']
        ctx['form'] = CaptchaAddForm(initial={'md5': captcha_id})
        ctx['captcha_image_url'] = self.captcha_image_url_template % captcha_id

        return self.render_to_response(ctx)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # TODO: Validate the answer against e-register
        image_content = ContentFile(requests.get(self.captcha_image_url_template % form.cleaned_data['md5']).content)
        self.object.image.save('%s_%s.png' % (self.object.answer, self.object.md5), image_content, False)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
