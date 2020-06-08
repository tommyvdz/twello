import json
import requests
import os
import uuid
from flask import current_app
from flask_babel import _

# not all languages are supported, and the translation api simply returns "bad request".
# This function enables a more meaningful answer
def supportedLanguage(source, dest):
    url = 'https://api-eur.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation'
    headers = {
        'X-ClientTraceId': str(uuid.uuid4())
    }
    response = requests.get(url).json()['translation']
    if source in response and dest in response:
        return True
    return False

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured')
    if not supportedLanguage(source_language, dest_language):
        return _('The translation service does not support this language')
    
    base_url = 'https://api-eur.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&from=' + source_language + '&to=' + dest_language
    constructed_url = base_url + path + params
    
    headers = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'westeurope',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text' : text
    }]
    response = requests.post(constructed_url, headers=headers, json=body)
    
    if response.status_code != 200:
        return _('Error: the translation service failed.')
    return response.json()[0]['translations'][0]['text']