mysms-xchat-plugin
==================

This project is meant soley to prevent me (and you) from having to use the browser application for MYSMS if you are using XChat as your IRC client. I use XChat at work and it is really annoying to switch back and forth from XChat to the browser to respond to texts.

With that said, here are some instructions to get started...

#### Quick Start Guide

##### Step 1.
Retrieve an API Key from the mysms.com folks. This step is kinda lengthy because you have to email and wait for their response. Another thing is that I am not sure how scalable this will be for them. I don't suspect lots of people will use this, so they should be ok with giving out a few API Keys (I hope :)).
##### Step 2.
Clone the repository to your local machine and change directories into it
##### Step 3.
Get the latest tag from stable with the following commands:

    git checkout stable
    git checkout v0.1

##### Step 4.
Copy the mysms folder from the src/ directory into your xchat directory. This can be done with the following command:
    
    cp mysms-xchat-plugin/src/com/csutherl/plugins/mysms ~/.xchat/

##### Step 5.
Create your local settings file (~/.mysms-settings.yaml or ~/.xchat/.mysms-settings.yaml). This file requries the following attributes at minimum:
    
  * logging_level: 10 # 10 for info, 20 for debug
  * api_key: $YOUR_API_KEY
  * accountMsisdn: $YOUR_MYSMS_NUMBER
  * accountPassword: $YOUR_MYSMS_PASSWORD

##### Step 6.
Start XChat, load the plugin, and use this command (in XChat) to start sending/receiving messages:
    
    /mysms $CONTACT_NAME_OR_CONTACT_PHONE_NUMBER
    
