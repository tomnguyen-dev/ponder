import requests
from PIL import Image
import speech_recognition as sr
import urllib.request
import os
import PySimpleGUI as sg
import re

# clear out previous file
if os.path.exists('temp.png'):
    os.remove('temp.png')

# scryfall API
url = 'https://api.scryfall.com/cards/named?exact='

BACKGROUND_COLOR = '#3E3C3C'

card_name='notion+thief'

class Card:
    def __init__(self, name, rules, oracle_text):
        self.name = name
        self.rules = rules
        self.oracle_text = oracle_text

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Say Card Name!')
        audio = r.listen(source)

    # recognize with Google Speech
    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio) + '\n--------------------------------------------------\n')
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def find_card():
    while True:
        # UNCOMMENT IN FINAL
        # user_input = get_audio()
        # card_name = user_input.replace(' ', '+').lower()

        response = requests.get(url+card_name + '&format=json')

        if response.status_code == 200:
            break

    card = Card(None, [], None)

    # rulings uri
    rulings_uri = response.json()['rulings_uri']
    rule_response = requests.get(rulings_uri)
    card.rules = rule_response.json()['data']

    # oracle text
    card.oracle_text = response.json()['oracle_text']

    # get image
    image_url = response.json()["image_uris"]["png"]
    urllib.request.urlretrieve(image_url, 'temp.png')

    return card

def process_ruling_text(card):
    rule_str = ''
    rule_cnt = 0

    for rule in card.rules:
        rule_cnt += 1
        rule_str = rule_str + ('\n> ' + rule['comment'] + '\n')

    return str(rule_cnt), rule_str


card = find_card()

rule_cnt, rule_str = process_ruling_text(card)

column = [
    [sg.Image('temp.png', key="-IMAGE-", background_color=BACKGROUND_COLOR)],

    [sg.Text('ORACLE TEXT', font='bold', background_color=BACKGROUND_COLOR)],
    [sg.Multiline(card.oracle_text, size=(60,5), key='-ORACLE-', text_color='white', font='bold', background_color=BACKGROUND_COLOR, no_scrollbar=True)],

    [sg.Text('\nRULES (' + rule_cnt + ')', font='bold', background_color=BACKGROUND_COLOR)],
    [sg.Multiline(rule_str, size=(60,10), key='-RULES-', text_color='white', font='bold', background_color=BACKGROUND_COLOR, no_scrollbar=True)]
]

layout = [
    [sg.Column(column, scrollable=True, vertical_scroll_only=True,background_color=BACKGROUND_COLOR)],

    [sg.Button('Voice Search', font='bold')]
]

window = sg.Window('Ponder', layout, background_color=BACKGROUND_COLOR, element_justification='c')

while True:
    event, values = window.read()

    if event == 'Voice Search':
        card = find_card()
        rule_cnt, rule_str = process_ruling_text(card)

        # refresh elements
        window['-IMAGE-'].update('temp.png')
        window['-ORACLE-'].update(card.oracle_text)
        window['-RULES-'].update(rule_str)
        window.refresh()

    if event == sg.WIN_CLOSED:
            break

