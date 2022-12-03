FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r /app/requirements.txt
