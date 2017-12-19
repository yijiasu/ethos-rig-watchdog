FROM python:alpine

############################
# USER CONFIGURABLE SETTINGS
############################

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

############################
# END OF USER CONFIG
############################

COPY ethos_monitor.py /working/
RUN pip install requests && \
    apk update && \
    apk add openssh-client sshpass

ENTRYPOINT ["/working/ethos_monitor.py"]
