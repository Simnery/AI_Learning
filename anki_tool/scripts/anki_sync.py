"""Sync JSON changes to Anki — only update specified fields, preserve audio.

Usage:
    python anki_sync.py ch1_cards.json Notes          # sync all Notes
    python anki_sync.py ch1_cards.json Notes Definition  # sync Notes + Definition
    python anki_sync.py ch1_cards.json Notes --word LLM  # sync only LLM
"""
import json, urllib.request, sys

ANKI = 'http://localhost:8765'

def anki(action, **params):
    body = json.dumps({'action': action, 'version': 6, 'params': params}).encode('utf-8')
    req = urllib.request.Request(ANKI, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

if len(sys.argv) < 3:
    print('Usage: python anki_sync.py FILE.json FIELD [FIELD...] [--word WORD]')
    print('Example: python anki_sync.py ch1_cards.json Notes')
    sys.exit(1)

path = sys.argv[1]
fields = [a for a in sys.argv[2:] if not a.startswith('--')]
target_word = None
if '--word' in sys.argv:
    idx = sys.argv.index('--word')
    target_word = sys.argv[idx + 1]

cards = json.load(open(path, 'r', encoding='utf-8'))
updated = 0
for c in cards:
    word = c['Word']
    if target_word and word != target_word:
        continue
    updates = {f: c.get(f, '') for f in fields}
    if not any(updates.values()):
        continue
    ids = anki('findNotes', query=f'Word:"{word}"')['result']
    if ids:
        anki('updateNoteFields', note={'id': ids[0], 'fields': updates})
        lens = {f: len(str(v)) for f, v in updates.items() if v}
        print(f'  {word}: updated {lens}')
        updated += 1
    else:
        print(f'  {word}: NOT FOUND in Anki')

print(f'\nSynced {updated} cards ({", ".join(fields)})')
