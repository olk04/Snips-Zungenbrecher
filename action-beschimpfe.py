#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import random
import os

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"


class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in
                self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()


def subscribe_intent_callback(hermes, intent_message):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intent_message, conf)


def random_line(afile):
    """ See Waterman's Reservoir Algorithm """

    line = next(afile)
    for num, aline in enumerate(afile, 2):
        if (random.randrange(num) == 0):
            line = aline
    return line


def action_wrapper(hermes, intent_message, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intent_message : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. 
      For end-user parameters use conf['secret']['parameterName'] 

    Refer to the documentation for further details. 
    """

    if(intent_message.slots is not None and len(intent_message.slots.name) >= 1):
        name = str(intent_message.slots.name.first().value)
    
        file = open(os.path.dirname(os.path.realpath(__file__)) + "/sprueche.txt")
        line = random_line(file)
        file.close()
    
        if (name.lower() in conf["secret"]["safe_names"]):
            result_sentence = "Das hättest du gerne. {} lässt dir ausrichten: {}".format(
                name, line)
        else:
            result_sentence = "Hey {}, {}".format(name, line)
    else:
        result_sentence = "Ich habe leider nicht verstanden wen ich beschimpfen soll."

    current_session_id = intent_message.session_id
    hermes.publish_end_session(current_session_id, result_sentence)


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("DANBER:beschimpfe", subscribe_intent_callback) \
            .start()
