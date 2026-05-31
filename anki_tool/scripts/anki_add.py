"""Add a single card to Anki — interactive or command-line. Stdlib only.

Usage:
    python anki_add.py                          # interactive mode
    python anki_add.py "Word" "Definition"      # quick add (auto-generates audio)
    python anki_add.py --json '{...}'            # add from JSON string

Fields: Word, Pronunciation, Audio, Definition, ExampleEN, ExampleCN, Notes
"""
import json, urllib.request, urllib.parse, hashlib, base64, sys

ANKI = 'http://localhost:8765'
MODEL = 'English Word'

def anki(action, **params):
    body = json.dumps({'action': action, 'version': 6, 'params': params}).encode('utf-8')
    req = urllib.request.Request(ANKI, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def download_tts(text, lang='en'):
    qs = urllib.parse.urlencode({'ie': 'UTF-8', 'client': 'tw-ob', 'tl': lang, 'q': text[:200]})
    req = urllib.request.Request(f'https://translate.google.com/translate_tts?{qs}',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()

def store_audio(text, prefix=''):
    safe = prefix[:20].replace(' ', '_').replace("'", "")
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    fname = f'{safe}_{h}.mp3'
    anki('storeMediaFile', filename=fname, data=base64.b64encode(download_tts(text)).decode('utf-8'))
    return f'[sound:{fname}]'

def add_card(deck, fields):
    """Add a single note. Returns note id or raises."""
    result = anki('addNote', note={
        'deckName': deck,
        'modelName': MODEL,
        'fields': fields,
        'tags': ['english']
    })
    if result.get('error'):
        raise RuntimeError(result['error'])
    return result['result']


if __name__ == '__main__':
    # List decks
    decks = anki('deckNames')['result']
    valid = [d for d in decks if d not in ['Default', '\u7cfb\u7edf\u9ed8\u8ba4']]
    deck = valid[0] if valid else 'Default'

    if '--json' in sys.argv:
        idx = sys.argv.index('--json')
        data = json.loads(sys.argv[idx + 1])
        word = data.get('Word', '')
        deck = data.pop('_deck', deck)
    elif len(sys.argv) >= 3:
        # Quick add: python anki_add.py "Word" "Definition"
        word = sys.argv[1]
        data = {'Word': word, 'Definition': sys.argv[2]}
        if len(sys.argv) >= 4:
            data['ExampleEN'] = sys.argv[3]
        if len(sys.argv) >= 5:
            data['ExampleCN'] = sys.argv[4]
    else:
        # Interactive
        print('Available decks:')
        for i, d in enumerate(valid, 1):
            print(f'  {i}. {d}')
        choice = input(f'\nSelect deck [1-{len(valid)}]: ').strip()
        if choice.isdigit() and 1 <= int(choice) <= len(valid):
            deck = valid[int(choice) - 1]
        print(f'Using deck: {deck}\n')

        word = input('Word: ').strip()
        if not word:
            print('Word is required.')
            sys.exit(1)
        pron = input('Pronunciation (IPA, enter to skip): ').strip()
        definition = input('Definition: ').strip()
        example_en = input('Example (EN): ').strip()
        example_cn = input('Example (CN): ').strip()
        notes = input('Notes: ').strip()
        data = {'Word': word, 'Pronunciation': pron, 'Definition': definition,
                'ExampleEN': example_en, 'ExampleCN': example_cn, 'Notes': notes}

    # Generate audio
    w = data.get('Word', '')
    tts_text = w.lower() if w == w.upper() and len(w) <= 5 else w
    try:
        data['Audio'] = store_audio(tts_text, 'word')
        print(f'Word audio: {data["Audio"]}')
    except Exception as e:
        print(f'Word audio failed: {e}')
        data['Audio'] = ''

    ex = data.get('ExampleEN', '')
    if ex and not ex.startswith('[sound:'):
        try:
            tag = store_audio(ex, 'sent')
            data['ExampleEN'] = f'{tag} {ex}'
            print(f'Sent audio: {tag}')
        except Exception as e:
            print(f'Sent audio failed: {e}')

    # Add
    data.setdefault('Pronunciation', '')
    data.setdefault('Definition', '')
    data.setdefault('ExampleEN', '')
    data.setdefault('ExampleCN', '')
    data.setdefault('Notes', '')
    data.setdefault('Audio', '')

    try:
        nid = add_card(deck, data)
        print(f'\nAdded: {word} (id={nid}) in deck "{deck}"')
    except RuntimeError as e:
        print(f'Failed: {e}')
