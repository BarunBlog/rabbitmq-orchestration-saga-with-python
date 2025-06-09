FROM python:3.14.0b2-alpine3.22

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "app.py"]