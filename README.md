# Experiment to hunt for stock tips on OMXT (Tallinn Stock Exchange)

## Running locally
`docker-compose up`

## Tests
`pytest`

## Production
- has separate docker-compose-live.yml that needs manual filling
- need to mount vision-credentials.json to <project>/rinja/
- good idea to mount <project>/media/

## Misc.
- positions are updated with a delay of some days (up to 3?)
- general stock listing price delay should be ~ 15 minutes
- scrape CAPTCHAS with the help of Google Vision: `python manage.py scrape_captcha_examples`
- train neural network: `python chaptcha.py train -i media/captchas/ -o my.net`
- try out neural network: `python chaptcha.py ocr -i media/captchas/2az6.png -n my.net`
- benchmark neural network: `python chaptcha.py ocr-bench -i media/captchas/ -n my.net` (latest result: 8.67% over ~3000 images)
