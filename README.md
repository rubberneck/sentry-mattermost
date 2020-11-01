# Sentry Mattermost
A plugin for Sentry to enable notifications to Mattermost Open Source Chat.
This is based in the sentry-slack plugin: https://github.com/getsentry/sentry-slack

![Example](example.png)

# Usage
Install with pip and enable the plugin in a Sentry Project:

     pip2.7 install -e git+https://github.com/Biekos/sentry-mattermost.git@master#egg=sentry-mattermost

You may need to install git:

    apt install git

If you are using the docker version of sentry you can enter the right container using: 

    docker exec -it sentry_onpremise_web_1  bash 


Configure Mattermost:
- Create an Incoming Webhook
- Enable override usernames and profile picture icons in System Console Integrations


# Contributing
We use Docker to setup a development stack. Make sure you have the latest
Docker Toolbox installed first.

### First time setup
Setups Docker containers and Sentry admin:

    make bootstrap restart

### Development
Each time you update the code, restart the containers:

    make restart

And access the sentry admin at

    http://<DOCKER IP>:8081
