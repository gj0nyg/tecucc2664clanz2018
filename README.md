# TECUCC-2664 at Cisco Live Melbourne 2018

This repository contains the code used in the API part of the session to demonstrate how to build a simple Cisco Spark Bot

## Install Docker
The easiest way to run the example Bot is to install Docker on your machine. The download of the free "Community Edition"
of Docker is available at https://www.docker.com/community-edition.

## Building the Docker image
To build the Docker image to run the bot simply execute this command from within the main directory of this repository:
```
docker build -t demobot .
```

After building the image executing the `docker images` command should give an output similar to this:
```
$ docker images
REPOSITORY                      TAG                 IMAGE ID            CREATED             SIZE
demobot                         latest              c547a293b625        44 hours ago        126MB
python                          3-alpine            29b5ce58cfbc        7 weeks ago         89.2MB
```

The `docker build` command created the `demobot` image using the specifications included in the `Dockerfile`.

## Create bot and obtain bot details
To be able to run your Bot you first have to create a bot on https://developer.ciscospark.com. 

After logging in 
* select "My Apps" in the upper right corner, 
* select the "+" icon in the upper right corner,
* click "Create a Bot"
* on the next page provide the required details for your bot
* click "Create Bot" at the bottom of the page

Make sure to collect the following details of your new Bot as they are required by the Python based demo bot.
* access token
* bot email address
* bot name

## Obtain credentials to access the Public Transport Victoria API

If you also want to use the [PTV API](https://www.ptv.vic.gov.au/about-ptv/data-and-reports/digital-products/ptv-timetable-api/) 
to obtain real-time information from Public Transport Victoria you will also need a developer ID and API key to access
that API. Instructions to obtain this is available here: https://static.ptv.vic.gov.au/PTV/PTV%20docs/API/1475462320/PTV-Timetable-API-key-and-signature-document.RTF

You basically have to send a request email and then typically will get your developer ID and API key within a few hours.

## Running the Docker image with the bot

Finally the prepared Docker image with the bot code can be executed with the following command:
```
docker run --name demobot -e DEMOBOT_ACCESS_TOKEN=<your access token> -e DEMOBOT_EMAIL=<your bot's email> -e DEMOBOT_NAME="<your bot's name>" -e PTV_API_USER=<your ptv api user> -e PTV_API_KEY=<your ptv api key> -d demobot
```

This command starts the demobot image and set the requirement variables from which the Python code reads the required information.

You will see an output similar to this:
```
$ ./start.sh 
68ea3008d11d3267635f2cb2e7be6f5c1ce18529ab357e628fc8cfed21e9a297
```

The `docker ps` command can be used to monitor the docker container:
```
$ docker ps
CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS               NAMES
68ea3008d11d        demobot             "python demobot.py"   30 seconds ago      Up 29 seconds                           demobot
```

To continously monitor the log created by the bot execute the `docker logs demobot -f` command:
```
$ docker logs demobot -f
Spark Bot Email: demobot_jkrohn@sparkbot.io
Spark Token: REDACTED
Found existing webhook.  Updating it.
Configuring Webhook. 
Webhook ID: Y2lzY29zcGFyazovL3VzL1dFQkhPT0svZjhlNGU3NjAtYWQ0OC00N2YyLWE2YzEtODNlY2Y5NDhkYmNk
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

The running Docker container can be stopped and removed by executing the `docker stop demobot` and `docker rm demobot`
commands.

With the bot Docker container running you can add the bot to a space via the bot's email address and start interacting with the bot.

In the bot log you you should be able to see notifications coming in through the bot's webhook:
```
$ docker logs demobot -f
Spark Bot Email: demobot_jkrohn@sparkbot.io
Spark Token: REDACTED
Found existing webhook.  Updating it.
Configuring Webhook. 
Webhook ID: Y2lzY29zcGFyazovL3VzL1dFQkhPT0svZjhlNGU3NjAtYWQ0OC00N2YyLWE2YzEtODNlY2Y5NDhkYmNk
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
Message content:
Message:
{
  "id": "Y2lzY29zcGFyazovL3VzL01FU1NBR0UvNjc2MmE5NTAtMjE4Yi0xMWU4LTk2NTQtNzU1MTUyMGJmODRh",
  "roomId": "Y2lzY29zcGFyazovL3VzL1JPT00vYWExMDc5YTItN2ZhYy0zZWQzLTlkMTgtZGNjNTc5MzNhNmNi",
  "roomType": "direct",
  "text": "/help",
  "personId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8wNzhkOGVjMi05Mjg5LTQ2NTUtOWE5NC0wNDNiOWVjMTMyOTk",
  "personEmail": "jkrohn@cisco.com",
  "created": "2018-03-06T22:12:05.349Z"
}
Message from: jkrohn@cisco.com
Found command: /help
127.0.0.1 - - [06/Mar/2018 22:12:09] "POST / HTTP/1.1" 200 -
Message content:
Message:
{
  "id": "Y2lzY29zcGFyazovL3VzL01FU1NBR0UvNjk2YWZjNzAtMjE4Yi0xMWU4LTk2NTQtNzU1MTUyMGJmODRh",
  "roomId": "Y2lzY29zcGFyazovL3VzL1JPT00vYWExMDc5YTItN2ZhYy0zZWQzLTlkMTgtZGNjNTc5MzNhNmNi",
  "roomType": "direct",
  "text": "Hello! I understand the following commands: /echo: Reply back with the same message sent. /help: Get help. /chuck: get Chuck Norris joke /traffic: show traffic cams /tram: show information about trams departing from MCEC stop /departures: show Melbourne airport departures",
  "personId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS84MjBmOTFjZi04ZmZhLTQ5MmQtYWM0OS1mNDQ0MmFiNmQ0NWU",
  "personEmail": "demobot_jkrohn@sparkbot.io",
  "markdown": "Hello!  I understand the following commands:  \n* **/echo**: Reply back with the same message sent. \n* **/help**: Get help. \n* **/chuck**: get Chuck Norris joke \n* **/traffic**: show traffic cams \n* **/tram**: show information about trams departing from MCEC stop \n* **/departures**: show Melbourne airport departures \n",
  "html": "<p>Hello!  I understand the following commands:<br></p><ul><li><strong>/echo</strong>: Reply back with the same message sent.</li><li><strong>/help</strong>: Get help.</li><li><strong>/chuck</strong>: get Chuck Norris joke</li><li><strong>/traffic</strong>: show traffic cams</li><li><strong>/tram</strong>: show information about trams departing from MCEC stop</li><li><strong>/departures</strong>: show Melbourne airport departures</li></ul>",
  "created": "2018-03-06T22:12:08.759Z"
}
Ignoring message from ourself
127.0.0.1 - - [06/Mar/2018 22:12:10] "POST / HTTP/1.1" 200 -
``` 

## Extend, start playing, have fun

Feel free to add similarily business critial functionality to the bot.

Some ideas:
* Arnold quotes: https://arnold-quotes-api.herokuapp.com/api.html
* quote of the day: https://favqs.com/api
* they said so API: https://quotes.rest/
* Lorem Picsum: https://picsum.photos/
* Pixabay: https://pixabay.com/api/docs/

***Have Fun!***

