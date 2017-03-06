FROM alpine:latest

RUN apk add --update \
    alpine-sdk \
    libffi-dev \
    openssl-dev \
    py-pip \
    python-dev

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

ADD *.py /
ADD config.json /

CMD ["python", "-u", "main.py"]
