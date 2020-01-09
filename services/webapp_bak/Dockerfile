FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY ./app /app
