import re
from unidecode import unidecode
from .numbers import normalize_numbers

# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# Lista de (expresión regular, reemplazo) para abreviaciones específicas en español
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('sra', 'señora'),
  ('sr', 'señor'),
  ('dr', 'doctor'),
  ('st', 'san'),  # para "san" como en "San José"
  ('co', 'compañía'),
  ('jr', 'junior'),
  ('lt', 'teniente'),
  ('cap', 'capitán'),
  # Agregar otras abreviaciones relevantes aquí
]]

def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text

def expand_numbers(text):
    return normalize_numbers(text)

def lowercase(text):
    return text.lower()

def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)

def convert_to_ascii(text):
    return unidecode(text)

def basic_cleaners(text):
    '''Pipeline básica que convierte a minúsculas y colapsa espacios en blanco sin transliteración.'''
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text

def spanish_cleaners(text):
    '''Pipeline para texto en español, incluyendo expansión de números y abreviaciones.'''
    text = convert_to_ascii(text)  # Opcional: elimina acentos y convierte a ASCII
    text = lowercase(text)
    text = expand_numbers(text)
    text = expand_abbreviations(text)
    text = collapse_whitespace(text)
    return text
