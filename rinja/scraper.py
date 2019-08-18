import bs4
import requests
from google.cloud import vision
from google.cloud.vision import types


class TallinnStockExchangeScraperClient:
    captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/et/shareholders'

    def __init__(self):
        self.google_vision_client = vision.ImageAnnotatorClient()

    def retrieve_captcha_input_and_session_pair(self):
        captcha_input = None
        session_id = None
        while not captcha_input or len(captcha_input) != 4:
            captcha_page = requests.get(self.captcha_retrieval_url)
            session_id = captcha_page.cookies['PHPSESSID']
            soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
            captcha_id = soup.select('#captcha-id')[0]['value']
            captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
            image_content = requests.get(captcha_image_url).content
            image_to_run_vision_on = types.Image(content=image_content)
            vision_response = self.google_vision_client.text_detection(image=image_to_run_vision_on)
            try:
                captcha_input = vision_response.text_annotations[0].description.strip()
            except IndexError:
                continue

        return captcha_input, session_id
