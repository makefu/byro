# Development

```
pip install docker-compose
## TODO: as of right now, only this fork contains updated docker-compose and settings file
git clone https://github.com/makefu/byro/
cd byro/src

# we need the db at startup
docker-compose build
docker-compose up -d db
docker-compose run --rm web migrate
docker-compose run --rm web createsuperuser
docker-compose run --rm web make_testdata
docker-compose up -d

$BROWSER http://127.0.0.1:8020
```
