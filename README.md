# ethos-rig-watchdog
This creates a docker container that checks the ethos dashboard for error conditions with each of the rigs
under that dashboard. If a matching error condition exists the appropriate remediation will be applied.

## The user configurable settings exist in the Dockerfile

```
# frequency in which status of minings rigs are checked in seconds (default 5 min)
ENV CHECK_FREQ 300

# max number of times a consecutive failure can occur before remote command execution (default 2)
ENV MAX_FAIL_COUNT 2

# dashboard url. make sure you use the json url (example: "http://rig.ethosdistro.com/?json=yes")
ENV DASHBOARD_URL "http://your-rig.ethosdistro.com/?json=yes"

# PUSHOVER (enable/disable)
ENV PUSHOVER disable

# PUSHOVER KEYS (setup account at pushover.net)
ENV APP_TOKEN <your token here>
ENV USER_KEY <your key here>

# Enable debug logging (enable/disable)
ENV DEBUG enable

# Conditions from ethos monitor json rig->condition that are considered ok and nothing should be done
# Space separated list "cond1 cond2 cond3 cond4"
ENV NON_ERROR_COND "mining just_booted high_load"

# Error conditions to act on with command executed via ssh
# Dictionary of conditions and remediations "cond1=remediation1,cond2=remediation2,cond3=remediation3"
ENV ERROR_REMEDIATIONS "no_hash=minestop"

# Default error remediation if nothing else matches in the form of a string "poweroff"
ENV ERROR_DEFAULT_REMEDIATION "r"
```
## Setup
 - Update the Dockerfile with your ethos dashboard url
 - If you want notifications you will need to obtain a http://pushover.net account
 - create a file called password in this directory and put your ethos user password in it (this is only needed for the first
 run in order to setup public private keys. You can delete it after the first run)
 - setup your own error/remediations if you like

## Running
Start and stop the docker container with the ```start.sh``` and ```stop.sh``` scripts. Everything is saved to the current
directory. If you make changes to the Dockerfile you will need to stop and start the container. If you delete the public
private keys you will need to add the password file again so the new keys can be propagated to the rigs.

## Program flow
A small off the shelf docker image (python:alpine) from dockerhub is loaded. User env variables are set and additional
packages are installed. The current directory is mounted to the container and it's also where you will find the log.

After container initialization the entrypoint script runs. The script checks to make sure that public private keys are setup.
These will also be created in this directory. The public keys are then copied to all the rigs pulled from the ethos dashboard. 
This is where the password file comes into play. If your uncomfortable with this step, you can copy the public keys manually
and skip creating the password file. 

The main loop starts at this point and checks the status of the rigs. If an error condition is detected a specified number of
times consecutively in a specified frequency of time, a remediation action is carried out on the rig in question via ssh. If you
have notifications setup you will get a message of this event as well. The loop will continue until the container is stopped.

## Notes
This is very beta and hasn't been fully tested
It is assumed that if you have multiple rigs, they all have the same password. 



