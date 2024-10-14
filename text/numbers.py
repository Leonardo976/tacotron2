import re
from num2words import num2words

# Expresiones regulares para distintos formatos de números
_comma_number_re = re.compile(r'([0-9][0-9\,]+[0-9])')
_decimal_number_re = re.compile(r'([0-9]+\.[0-9]+)')
_euros_re = re.compile(r'€([0-9\,]*[0-9]+)')
_dollars_re = re.compile(r'\$([0-9\.\,]*[0-9]+)')
_ordinal_re = re.compile(r'[0-9]+(o|a)')
_number_re = re.compile(r'[0-9]+')

def _remove_commas(m):
    return m.group(1).replace(',', '')

def _expand_decimal_point(m):
    return m.group(1).replace('.', ' punto ')

def _expand_euros(m):
    match = m.group(1)
    parts = match.split('.')
    euros = int(parts[0].replace(',', '')) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if euros and cents:
        euro_unit = 'euro' if euros == 1 else 'euros'
        cent_unit = 'centavo' if cents == 1 else 'centavos'
        return f'{euros} {euro_unit}, {cents} {cent_unit}'
    elif euros:
        euro_unit = 'euro' if euros == 1 else 'euros'
        return f'{euros} {euro_unit}'
    elif cents:
        cent_unit = 'centavo' if cents == 1 else 'centavos'
        return f'{cents} {cent_unit}'
    else:
        return 'cero euros'

def _expand_ordinal(m):
    return num2words(int(m.group(0)), to='ordinal', lang='es')

def _expand_number(m):
    return num2words(int(m.group(0)), lang='es')

def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_euros_re, _expand_euros, text)
    text = re.sub(_dollars_re, _expand_euros, text)  # Usar la misma función para euros
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
