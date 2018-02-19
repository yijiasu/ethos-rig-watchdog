#!/usr/bin/env  python3

import requests
import os
import time
import logging
import http.client
import urllib
from collections import defaultdict
import config

# pushover keys
app_token = config.APP_TOKEN
user_key = config.USER_KEY
pushover = config.PUSHOVER

# default logging level
if config.DEBUG == 'enable':
    log_level = logging.DEBUG
else:
    log_level = logging.ERROR


logging.basicConfig(filename='ethos_monitor.log', level=log_level, format='%(asctime)s %(message)s')

# error conditions
non_error_conditions = config.NON_ERROR_COND.split()
error_remediations_str = config.ERROR_REMEDIATIONS
error_remediations = dict(x.split('=') for x in error_remediations_str.split(','))
error_default_remediation = config.ERROR_DEFAULT_REMEDIATION


dashboard_url = config.DASHBOARD_URL
freq = int(config.CHECK_FREQ)
max_fail_count = int(config.MAX_FAIL_COUNT)

def send_push(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": app_token,
                     "user": user_key,
                     "message": msg,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()


def setup_ssh():
    if not os.path.exists('.ssh/id_rsa') and not os.path.exists('.ssh/id_rsa.pub'):
        os.system("ssh-keygen -f .ssh/id_rsa -t rsa -N ''")
    data = requests.get(dashboard_url).json()
    rigs = data['rigs'].keys()
    for rig in rigs:
        rig_ip = (data['rigs'][rig]['ip'])
        if os.system("ssh -oBatchMode=yes -i .ssh/id_rsa -oStrictHostKeyChecking=no ethos@" + rig_ip + " exit"):
            os.system("sshpass -f password ssh-copy-id -i .ssh/id_rsa.pub -oStrictHostKeyChecking=no ethos@" + rig_ip)


def main():
    fail_count = defaultdict(int)
    if pushover == 'enable':
        send_push("Starting Ethos Monitoring")

    # setup_ssh()

    while True:
        try:
            data = requests.get(dashboard_url).json()
            rigs = data['rigs'].keys()

            for rig in rigs:
                rig_condition = data['rigs'][rig]['condition']
                logging.debug("non error conditions: %s" % non_error_conditions)
                logging.debug("error remediations: %s" % error_remediations)
                logging.debug("default error remediation: %s" % error_default_remediation)
                if rig_condition not in non_error_conditions:
                    fail_count[rig] += 1
                    logging.debug("fail count for %s is %s" % (rig, fail_count[rig]))
                    logging.debug("condition is: %s" % rig_condition)
                    logging.debug(data)
                    if fail_count[rig] >= max_fail_count:
                        ip = (data['rigs'][rig]['ip'])
                        logging.debug("rig ip: %s" % ip)
                        if rig_condition in error_remediations:
                            command = error_remediations.get(rig_condition)
                        else:
                            command = error_default_remediation
                        os.system("ssh -i .ssh/id_rsa ethos@" + ip + " -oStrictHostKeyChecking=no " + command)
                        logging.error("rig %s failed with condition: %s" % (rig, rig_condition))
                        logging.error("executing %s on rig with ip %s" % (command, ip))
                        logging.error(data)
                        if pushover == 'enable':
                            logging.error("sending pushover notification...")
                            send_push("rig %s failed with condition: %s" % (rig, rig_condition))
                        fail_count[rig] = 0
                else:
                    logging.debug("all is good with %s " % rig)
                    fail_count[rig] = 0
            time.sleep(freq)
        except:
            #ignore anything...


if __name__ == '__main__':
    main()
