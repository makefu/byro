# Development

```
pip install docker-compose
git clone https://github.com/byro/byro/
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
