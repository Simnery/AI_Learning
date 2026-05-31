"""Fix missing full-term audio for acronym cards. Also fix definitions that have wrong/missing English terms.

Usage:
    cd anki_tool && python scripts/anki_fix_acronyms.py           # fix ALL acronyms
    cd anki_tool && python scripts/anki_fix_acronyms.py --dry-run  # preview
    cd anki_tool && python scripts/anki_fix_acronyms.py --word MCP # fix single
"""
import json, re, hashlib, base64, sys, time
import urllib.request, urllib.parse

ANKI = 'http://localhost:8765'

# Known acronym mappings: acronym -> full English term
# Used when the definition doesn't contain the correct English full term
KNOWN = {
    'A2A': 'Agent-to-Agent Protocol',
    'ANN': 'Approximate Nearest Neighbor',
    'AIGC': 'AI Generated Content',
    'ASR': 'Automatic Speech Recognition',
    'ATC': 'Ascend Tensor Compiler',
    'ACL': 'Ascend Computing Library',
    'BLEU': 'Bilingual Evaluation Understudy',
    'BM25': 'Best Matching 25',
    'CANN': 'Compute Architecture for Neural Networks',
    'CLIP': 'Contrastive Language-Image Pre-training',
    'CNN': 'Convolutional Neural Network',
    'CORS': 'Cross-Origin Resource Sharing',
    'COCO': 'Common Objects in Context',
    'DAG': 'Directed Acyclic Graph',
    'DPO': 'Direct Preference Optimization',
    'DSL': 'Domain-Specific Language',
    'EDA': 'Exploratory Data Analysis',
    'FAISS': 'Facebook AI Similarity Search',
    'FPN': 'Feature Pyramid Network',
    'FSDP': 'Fully Sharded Data Parallel',
    'FP16': '16-bit Floating Point',
    'GELU': 'Gaussian Error Linear Unit',
    'GPT': 'Generative Pre-trained Transformer',
    'GPU': 'Graphics Processing Unit',
    'JWT': 'JSON Web Token',
    'LCEL': 'LangChain Expression Language',
    'LLM': 'Large Language Model',
    'MCP': 'Model Context Protocol',
    'MTEB': 'Massive Text Embedding Benchmark',
    'NCCL': 'NVIDIA Collective Communications Library',
    'NF4': 'Normal Float 4-bit',
    'NLP': 'Natural Language Processing',
    'NMS': 'Non-Maximum Suppression',
    'NPU': 'Neural Processing Unit',
    'OCR': 'Optical Character Recognition',
    'ONNX': 'Open Neural Network Exchange',
    'OOM': 'Out of Memory',
    'PEFT': 'Parameter-Efficient Fine-Tuning',
    'PPO': 'Proximal Policy Optimization',
    'QPS': 'Queries Per Second',
    'RAG': 'Retrieval-Augmented Generation',
    'RAGAS': 'Retrieval Augmented Generation Assessment',
    'RDMA': 'Remote Direct Memory Access',
    'RLHF': 'Reinforcement Learning from Human Feedback',
    'ROUGE': 'Recall-Oriented Understudy for Gisting Evaluation',
    'RRF': 'Reciprocal Rank Fusion',
    'SAHI': 'Slicing Aided Hyper Inference',
    'SFT': 'Supervised Fine-Tuning',
    'SJF': 'Shortest Job First',
    'SVD': 'Singular Value Decomposition',
    'TDP': 'Thermal Design Power',
    'TPOT': 'Time Per Output Token',
    'TTFT': 'Time To First Token',
    'TTS': 'Text-to-Speech',
    'TRL': 'Transformer Reinforcement Learning',
    'VLM': 'Vision Language Model',
    'VRAM': 'Video Random Access Memory',
    'YOLO': 'You Only Look Once',
}

def anki(action, **params):
    body = json.dumps({'action': action, 'version': 6, 'params': params}).encode('utf-8')
    req = urllib.request.Request(ANKI, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def download_tts(text):
    for _ in range(2):
        try:
            qs = urllib.parse.urlencode({'ie':'UTF-8','client':'tw-ob','tl':'en','q':text[:200]})
            req = urllib.request.Request(f'https://translate.google.com/translate_tts?{qs}', headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                d = resp.read()
                if len(d) > 100: time.sleep(1.5); return d
        except: time.sleep(1)
    qs = urllib.parse.urlencode({'audio': text[:100], 'type': 2})
    req = urllib.request.Request(f'https://dict.youdao.com/dictvoice?{qs}', headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()

def store_audio(text, prefix=''):
    safe = prefix[:20].replace(' ','_').replace("'","")
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    fname = f'full_{safe}_{h}.mp3'
    anki('storeMediaFile', filename=fname, data=base64.b64encode(download_tts(text)).decode('utf-8'))
    return f'[sound:{fname}]'

dry = '--dry-run' in sys.argv
target = None
if '--word' in sys.argv:
    idx = sys.argv.index('--word')
    target = sys.argv[idx + 1]

ids = anki('findNotes', query='*')['result']
infos = anki('notesInfo', notes=ids)['result']
fixed_audio, fixed_def = 0, 0

for n in infos:
    word = n['fields']['Word']['value']
    if target and word != target: continue
    if not (word == word.upper() and len(word) <= 5): continue
    nid = n['noteId']
    definition = n['fields']['Definition']['value']

    # Check 1: already has [sound:...] in first 15 chars? Skip.
    if '[sound:' in definition[:15]:
        continue

    # Check 2: extract English full term from definition
    # Try pattern: EnglishTerm（中文） at the start
    m = re.match(r'([A-Za-z][A-Za-z\-\s]{2,60})[（(]', definition)
    if not m:
        # Fallback: look up known mapping
        if word in KNOWN:
            full_term = KNOWN[word]
        else:
            continue
    else:
        full_term = m.group(1).strip()

    if dry:
        status = 'ADD AUDIO' if m else 'FIX DEF'
        print(f'  {status:10s} {word:6s} -> {full_term[:50]}')
        if m: fixed_audio += 1
        else: fixed_def += 1
        continue

    # Fix Definition if needed
    if not m and word in KNOWN:
        # Replace incorrect English term in definition
        old_eng = re.match(r'^([A-Za-z\s\-]+)（', definition)
        if old_eng and old_eng.group(1) != full_term:
            definition = definition.replace(old_eng.group(1), full_term, 1)
        elif not old_eng:
            # No English term at all — prepend
            definition = f'{full_term}（{definition}'
        fixed_def += 1

    # Add TTS audio
    try:
        tag = store_audio(full_term, word)
        new_def = f'{tag} {definition}'
        anki('updateNoteFields', note={'id': nid, 'fields': {'Definition': new_def}})
        print(f'  {word}: +{tag} ({full_term[:40]})')
        fixed_audio += 1
    except Exception as e:
        print(f'  {word}: TTS FAILED ({e})')

if dry:
    print(f'\nAdd audio: {fixed_audio}  Fix def: {fixed_def}')
else:
    print(f'\nFixed {fixed_audio} audio + {fixed_def} definitions.')
