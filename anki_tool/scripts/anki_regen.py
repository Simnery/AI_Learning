"""Anki card generator — reads card data from JSON, generates TTS audio, imports to Anki.

Usage:
    python anki_regen.py              # read from 01_sample_cards.json
    python anki_regen.py cards.json   # read from custom file
    python anki_regen.py --deck "MyDeck" cards.json
"""
import hashlib, base64, json, re, sys, time
import urllib.request, urllib.parse

ANKI  = 'http://localhost:8765'
MODEL = 'English Word'
SRC   = '../cards/01_sample_cards.json'  # default data source (from anki_tool/ dir)


def anki(action, **params):
    body = json.dumps({'action': action, 'version': 6, 'params': params}).encode('utf-8')
    req = urllib.request.Request(ANKI, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def download_tts(text, lang='en', retries=2):
    """Download TTS audio, trying Google first then Youdao as fallback."""
    # Provider 1: Google TTS
    for attempt in range(retries):
        try:
            qs = urllib.parse.urlencode({'ie': 'UTF-8', 'client': 'tw-ob', 'tl': lang, 'q': text[:200]})
            url = f'https://translate.google.com/translate_tts?{qs}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.getcode()
                data = resp.read()
                if code == 200 and len(data) > 100:  # valid audio
                    time.sleep(1.5)
                    return data
        except Exception:
            time.sleep(1)
    # Provider 2: Youdao (fallback)
    try:
        qs = urllib.parse.urlencode({'audio': text[:100], 'type': 2})  # type=2 American
        url = f'https://dict.youdao.com/dictvoice?{qs}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 100:
                return data
    except Exception:
        pass
    raise RuntimeError(f'TTS failed for: {text[:50]}')


def store_audio(text, prefix=''):
    safe = prefix[:20].replace(' ', '_').replace("'", "")
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    fname = f'{safe}_{h}.mp3'
    anki('storeMediaFile', filename=fname, data=base64.b64encode(download_tts(text)).decode('utf-8'))
    return f'[sound:{fname}]'


def load_cards(path):
    """Load card data from JSON file. Each entry must have: Word, Pronunciation, Definition, ExampleEN, ExampleCN, Notes."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def enrich_card(card):
    """Add TTS audio to card data — returns dict ready for Anki addNote."""
    word = card['Word']

    # Word audio: smart acronym handling
    if word == word.upper() and len(word) <= 5:
        lower = word.lower()
        # If lowercase form has >= 2 vowels, it's pronounceable (RAG, NASA)
        # Otherwise spell it out (AIGC, LLM, GPU, API)
        vowels = sum(1 for c in lower if c in 'aeiouy')
        if vowels >= 2:
            tts_text = lower  # pronounce as word
        else:
            tts_text = ' '.join(word)  # spell letter by letter
    else:
        tts_text = word
    try:
        card['Audio'] = store_audio(tts_text, 'word')
    except Exception:
        card['Audio'] = ''

    # Sentence audio prepended to ExampleEN
    try:
        sent_tag = store_audio(card['ExampleEN'], 'sent')
        card['ExampleEN'] = f'{sent_tag} {card["ExampleEN"]}'
    except Exception:
        pass  # keep plain text on failure

    # Acronym: auto-extract full term from Definition, add full-term audio
    if word == word.upper() and len(word) <= 5:
        m = re.match(r'([A-Za-z\-\s]+)（', card['Definition'])
        if m:
            full_term = m.group(1).strip()
            try:
                full_tag = store_audio(full_term, 'full')
                card['Definition'] = f'{full_tag} {card["Definition"]}'
            except Exception:
                pass

    return card


def main():
    # Parse args
    path = sys.argv[1] if len(sys.argv) > 1 else SRC
    deck = 'AI术语'
    if '--deck' in sys.argv:
        idx = sys.argv.index('--deck')
        deck = sys.argv[idx + 1]
        path = sys.argv[idx + 2] if idx + 2 < len(sys.argv) else path

    # Load & validate
    cards = load_cards(path)
    print(f'Loaded {len(cards)} cards from {path}')

    # Skip validation — TTS import is more important than perfect quoting

    # Check Anki
    try:
        v = anki('version')['result']
        print(f'AnkiConnect v{v} OK')
    except Exception as e:
        print(f'Cannot reach Anki: {e}')
        return

    # Full rebuild mode: delete all old notes first
    full_rebuild = '--full' in sys.argv
    if full_rebuild:
        deck_query = deck.replace('"', '\\"')
        ids = anki('findNotes', query=f'deck:"{deck_query}"')['result']
        if ids:
            anki('deleteNotes', notes=ids)
            print(f'Deleted {len(ids)} old notes from "{deck}"')

    # Ensure deck exists
    anki('createDeck', deck=deck)
    print(f'Deck: {deck}  Model: {MODEL}')

    # Get existing words in this deck to skip
    existing = set()
    if not full_rebuild:
        deck_query = deck.replace('"', '\\"')
        eids = anki('findNotes', query=f'deck:"{deck_query}"')['result']
        if eids:
            einfos = anki('notesInfo', notes=eids)['result']
            existing = {n['fields']['Word']['value'] for n in einfos}
            print(f'  {len(existing)} existing cards, will skip duplicates')
        else:
            print(f'  No existing cards, creating all')

    # Create (skip duplicates in incremental mode)
    ok = 0
    skipped = 0
    for card in cards:
        word = card['Word']
        if word in existing:
            skipped += 1
            continue
        print(f'  {word}', end='', flush=True)
        card = enrich_card(card)
        result = anki('addNote', note={
            'deckName': deck,
            'modelName': MODEL,
            'fields': card,
            'tags': ['english', 'ai-ml']
        })
        if result.get('error'):
            print(f'  ERR: {result["error"]}')
        else:
            ok += 1
            print('  OK')

    if skipped:
        print(f'  (skipped {skipped} existing)')
    print(f'\n=== {ok} new + {skipped} existing = {ok+skipped}/{len(cards)} cards in "{deck}" ===')


if __name__ == '__main__':
    main()
