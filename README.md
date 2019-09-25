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
