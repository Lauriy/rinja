![Python application](https://github.com/Lauriy/rinja/workflows/Rinja/badge.svg)

# Experiment to hunt for stock tips on OMXT (Tallinn Stock Exchange)

## Running locally
`docker-compose up`

## Tests
`pytest`

## Production
- has separate docker-compose-live.yml that needs manual filling
- need to mount vision.json to <project>/rinja/credentials/
- mount <project>/media/
- mount <project>/static-collected/

## Misc.
- positions are updated with a delay of some days (up to 3?)
- general stock listing price delay should be ~ 15 minutes
- default root user: `python manage.py loaddata rinja/fixtures/auth_user.json` or create one with `python manage.py createsuperuser`
- static list of stocks: `python manage.py loaddata rinja/fixtures/rinja_stock.json`
- scrape CAPTCHAS with the help of Google Vision: `python manage.py scrape_captcha_examples`

## Currently unavailable without some work
- train neural network: `python chaptcha.py train -i media/captchas/ -o my.net`
- try out neural network: `python chaptcha.py ocr -i media/captchas/2az6.png -n my.net`
- benchmark neural network: `python chaptcha.py ocr-bench -i media/captchas/ -n my.net` (latest result: 8.67% over ~3000 images)
