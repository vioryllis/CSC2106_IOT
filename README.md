# CSC2106_IOT

## django app as server + frontend dashboard for t14's iot project
```
create your own venv
create your own .env file inside iot folder and paste this inside:

# Postgres database settings
POSTGRES_DATABASE_NAME = 'iotfarmer'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '1234'
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'

remember to change to your own db details
```
```
cd into iot and 'pip install -r requirements.txt'
remember to run 'python manage.py migrate'
```

run the app: cd into iot
```
py manage.py runserver 0.0.0.0:8000
```

m5stick codes are in the m5stick folder, remember to change configs & topics

mesh codes are in the mesh folder
## ty