FROM alpine:3.18

ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql gzip bash && apk add python3 py3-pip && pip3 install --no-cache --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY utils/ /app/utils/
COPY chmfc.py /app/

CMD ["python", "/app/chmfc.py"]
