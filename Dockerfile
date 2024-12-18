FROM python:3.13

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install gunicorn~=22.0.0
RUN pip install -r requirements.txt

COPY src/ /code

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "main:app"]
