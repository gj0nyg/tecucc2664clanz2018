FROM python:3-alpine

# install ngrok
RUN set -ex \
  && apk add --no-cache --virtual .build-deps wget \
  && apk add --no-cache ca-certificates \
  \
  && cd /tmp \
  && wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip \
  && unzip ngrok-stable-linux-amd64.zip \
  && install -v -D ngrok /bin/ngrok \
  && rm -f ngrok-stable-linux-amd64.zip ngrok \
  \
  && apk del .build-deps

# Install Pythin dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

# Create bot directory and add code
RUN mkdir /bot
WORKDIR /bot
ADD ./*.py /bot/

# Run Bot
CMD [ "python", "demobot.py" ]
