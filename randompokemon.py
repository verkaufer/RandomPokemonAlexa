from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

ASK_APPLICATION_ID = None # TODO: replace with real application id

ENDPOINT = "http://randompokemongenerator.com/api"

app = Flask(__name__)
ask = Ask(app, "/")

request_mappings = {
    'num_pokemon': 'Count',
    'region': 'Region',
    'type': 'Type'
}

@ask.launch
def launch():
    launch_text = render_template('welcome')
    return question(launch_text)

@ask.intent("GetPokemon", mapping=request_mappings)
def oneshot_pokemon():
    """
    Returns one or more Pokemon based on default generator values
    """
    pass

@ask.intent("GetSpecificPokemon")
def get_random_pokemon():
    """
    Uses user-provided slots to request random pokemon that meet constraints from slots
    """
    pass

def _send_api_request():
    """
    Helper method to send the actual POST request to API
    """
    pass