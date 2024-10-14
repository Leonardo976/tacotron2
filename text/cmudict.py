import re

# Símbolos válidos para el español, incluyendo la "ñ"
valid_symbols = [
    'AA', 'AE', 'AH', 'IY', 'OW', 'P', 'T', 'K', 'S', 'D', 'N', 
    'M', 'R', 'L', 'F', 'B', 'G', 'Y', 'W', 'Z', 'Ñ'
]

_valid_symbol_set = set(valid_symbols)

class SpanishDict:
    '''Wrapper para un diccionario de pronunciaciones en español.'''
    def __init__(self, file_or_path, keep_ambiguous=True):
        if isinstance(file_or_path, str):
            with open(file_or_path, encoding='utf-8') as f:
                entries = _parse_spanishdict(f)
        else:
            entries = _parse_spanishdict(file_or_path)
        if not keep_ambiguous:
            entries = {word: pron for word, pron in entries.items() if len(pron) == 1}
        self._entries = entries

    def __len__(self):
        return len(self._entries)

    def lookup(self, word):
        '''Devuelve una lista de pronunciaciones en español para la palabra dada.'''
        return self._entries.get(word.lower())

_alt_re = re.compile(r'\([0-9]+\)')

def _parse_spanishdict(file):
    spanishdict = {}
    for line in file:
        if len(line) and (line[0] >= 'A' and line[0] <= 'Z' or line[0] == "'"):
            parts = line.split('  ')
            word = re.sub(_alt_re, '', parts[0])
            pronunciation = _get_pronunciation(parts[1])
            if pronunciation:
                if word in spanishdict:
                    spanishdict[word].append(pronunciation)
                else:
                    spanishdict[word] = [pronunciation]
    return spanishdict

def _get_pronunciation(s):
    parts = s.strip().split(' ')
    for part in parts:
        if part not in _valid_symbol_set:
            return None
    return ' '.join(parts)
