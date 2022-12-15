from flask import Flask, jsonify, request
from os.path import exists
import base64
import json
from pygame import mixer
import platform
import os

app = Flask(__name__)

def play_sound(sound_classification):

    """
    String as uppercase colour matching value in dictionary - Plays a sound matching colour to file
    """

    mixer.init()

    # Matches colour to a sound file
    sound_dict = {
        "GREEN": "sounds/most_wonderful_time.wav",
        "AMBER": "sounds/business_will_comsume.wav",
        "RED": "sounds/christmas-is-cancelled.wav",
    }

    if sound_classification not in sound_dict:
        # No Colour to sound file found
        return
    else:
        print("Playing sound - {}".format(sound_dict[sound_classification]))
        sound_fx = mixer.Sound(sound_dict[sound_classification])

    return sound_fx.play()

def change_lights(colour):

    """
    Change the LED Colour and flash lights to alert

    To control LEDs on Raspberry Pi requires sudo access (move to SPI GPIO10 not a fix as colour issues)
    Gunicorn cannot run as sudo meaning function required executing outside code - also means can execute as background
    task easily so flashing lights does not delay the HTTP response. Only execute on Rasp Pi.
    """

    if platform.node() == "raspberrypi":
        # gives ability to run code without crashing on other systems
        os.system('sudo python led_control.py {} flash &'.format(colour))
    else:
        return
    return

def read_status():

    """
    Check the status file exists - created after initially running
    """

    if not exists("status.json"):
        print("File Missing! - Please run initial vManage poll")
        return {}
    else:
        # Open json - return as dict
        f = open("status.json", "r")
        status_json = json.loads(f.read())
        f.close()
        return status_json


def write_status(new_status):
    f = open("status.json", "w")
    f.write(json.dumps(new_status, indent=2))
    f.close()


def webhook_auth(offered):

    """
    vManage sends webhook with Basic Authentication which is a base64 representation of "username:password"
    """
    try:
        # Get username/password from ENVs
        username = os.environ['WEBHOOK_USERNAME']
        password = os.environ['WEBHOOK_PASSWORD']
    except Exception as e:
        # If none exist, default to test/test
        print("Credentials Error: {}".format(e))
        username = 'test'
        password = 'test'

    try:
        unpw_bytes = "{}:{}".format(username, password).encode()
        basic_auth = base64.b64encode(unpw_bytes)
        if offered.split()[1] == basic_auth.decode():
            return True
        else:
            return False
    except Exception as e:
        print("Authentication Error: {}".format(e))
        return False


def tree_status(status_dict):

    """
    Pass the status dictionary and process what state the tree should be in
    """

    colour = "GREEN"

    for s in status_dict:
        # Cycle through the dictionary to see if any are unreachable
        if status_dict[s] == "unreachable":
            colour = "RED"

    play_sound(colour)
    change_lights(colour)

    return colour


def process_event(new_request):

    """
    Takes in the webhook - validates the format and determines the actions to take
    """

    if "message" in new_request.json and "system_ip" in new_request.json:
        message = new_request.json["message"]
        system_ip = new_request.json["system_ip"]
    else:
        # not the format we were expecting
        return

    # Only looking for webhooks with the messages below

    if message == "Control connections for the node came up":
        print("Message: {} - {} - moving to state to reachable".format(message, system_ip))
        new_state = "reachable"
    elif message == "All Control connections for the node are down":
        print("Message: {} - {} - moving to state to unreachable".format(message, system_ip))
        new_state = "unreachable"
    else:
        # This is not the webhook we are looking for
        return

    status_dict = read_status()
    status_dict[system_ip] = new_state

    tree_colour = tree_status(status_dict)
    write_status(status_dict)
    print("Tree state: {}".format(tree_colour))
    return


@app.route('/webhook/', methods=['POST'])
def webhook():

    """ Receiving webhook, authorising and then processing """

    print("## Method: POST - Webhook Received ## ")
    if not webhook_auth(request.headers.get('Authorization')):
        return jsonify({'status': 'Not Authorized'}), 403

    if request.headers.get('Content-Type') == 'application/json':
        process_event(request)

    return jsonify({'status': 'completed'}), 201


@app.route('/webhook/', methods=['GET'])
def webhook_get():
    # Only including to test web server is reachable
    print("## Method: GET - Webhook Received ## ")
    return "This works!", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
