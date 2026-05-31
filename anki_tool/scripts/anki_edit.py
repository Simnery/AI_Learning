"""Edit existing Anki cards — update any field on any note. Stdlib only.

Usage:
    python anki_edit.py                          # interactive mode
    python anki_edit.py "RAG" --audio ""         # regenerate audio for RAG
    python anki_edit.py "RAG" --def "new text"   # update Definition
    python anki_edit.py "RAG" --field Definition --value "new text"
    python anki_edit.py --list                   # list all cards with fields
"""
import json, urllib.request, urllib.parse, hashlib, base64, sys

ANKI = 'http://localhost:8765'

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

def find_card(word):
    """Find a card by Word field. Returns (note_id, fields_dict) or None."""
    deck_query = urllib.parse.quote(word)
    ids = anki('findNotes', query=f'Word:"{word}"')['result']
    if not ids:
        return None
    info = anki('notesInfo', notes=ids[:1])['result'][0]
    return info['noteId'], {k: v['value'] for k, v in info['fields'].items()}

def list_all():
    """List all cards with their fields."""
    ids = anki('findNotes', query='*')['result']
    if not ids:
        print('No cards found.')
        return
    info = anki('notesInfo', notes=ids)['result']
    for n in info:
        f = n['fields']
        print(f'  [{n["noteId"]}] {f["Word"]["value"]}')
        for k, v in f.items():
            if k != 'Word' and v['value']:
                preview = v['value'][:80].replace('\n', ' ')
                print(f'    {k}: {preview}')
        print()

def edit_card(word, updates):
    """Update fields on an existing card."""
    result = find_card(word)
    if not result:
        print(f'Card "{word}" not found.')
        return False
    nid, _ = result
    anki('updateNoteFields', note={'id': nid, 'fields': updates})
    print(f'Updated "{word}": {list(updates.keys())}')
    return True


if __name__ == '__main__':
    if '--list' in sys.argv:
        list_all()
        sys.exit(0)

    if len(sys.argv) < 2:
        print('Usage: python anki_edit.py WORD [--field KEY --value VAL] [--audio ""] [--def "text"] [--list]')
        print('Examples:')
        print('  python anki_edit.py RAG --audio ""         # regenerate audio')
        print('  python anki_edit.py RAG --def "new text"   # update definition')
        print('  python anki_edit.py --list                 # list all cards')
        sys.exit(0)

    word = sys.argv[1]
    updates = {}
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--audio':
            override = args[i+1] if i+1 < len(args) and not args[i+1].startswith('--') else ''
            if override:
                tts_text = override
                i += 2
            elif word == word.upper() and len(word) <= 5:
                lower = word.lower()
                vowels = sum(1 for c in lower if c in 'aeiouy')
                tts_text = lower if vowels >= 2 else ' '.join(word)
                i += 1
            else:
                tts_text = word
                i += 1
            tag = store_audio(tts_text, 'word')
            updates['Audio'] = tag
            print(f'Generated audio ({tts_text}): {tag}')
        elif args[i] == '--field' and i + 2 < len(args):
            updates[args[i + 1]] = args[i + 2]
            i += 3
        elif args[i] == '--def' and i + 1 < len(args):
            updates['Definition'] = args[i + 1]
            i += 2
        elif args[i] == '--example' and i + 1 < len(args):
            text = args[i + 1]
            tag = store_audio(text, 'sent')
            updates['ExampleEN'] = f'{tag} {text}'
            i += 2
        else:
            i += 1

    if not updates:
        # Interactive mode
        result = find_card(word)
        if not result:
            print(f'Card "{word}" not found.')
            sys.exit(1)
        nid, fields = result
        print(f'Editing: {word}')
        print(f'  Pronunciation: {fields.get("Pronunciation","")}')
        print(f'  Definition:    {fields.get("Definition","")[:80]}')
        print(f'  ExampleEN:     {fields.get("ExampleEN","")[:80]}')
        print(f'  ExampleCN:     {fields.get("ExampleCN","")[:80]}')
        print()
        print('Available quick actions:')
        print('  1. Regenerate word audio  (python anki_edit.py "' + word + '" --audio "")')
        print('  2. Regenerate sent audio  (python anki_edit.py "' + word + '" --example "new sentence"')
        print('  For full updates use: python anki_edit.py "' + word + '" --field FIELD_NAME "new value"')
        sys.exit(0)

    edit_card(word, updates)
