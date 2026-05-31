"""Manage Anki note types — view, add fields, update templates. Stdlib only.

Usage:
    python anki_model.py                        # list all models + fields
    python anki_model.py English Word           # show model details
    python anki_model.py English Word --add Etymology  # add a new field
"""
import json, urllib.request, sys

ANKI = 'http://localhost:8765'

def anki(action, **params):
    body = json.dumps({'action': action, 'version': 6, 'params': params}).encode('utf-8')
    req = urllib.request.Request(ANKI, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def list_models():
    models = anki('modelNames')['result']
    for m in models:
        fields = anki('modelFieldNames', modelName=m)['result']
        print(f'{m} ({len(fields)} fields): {fields}')

def show_model(name):
    try:
        fields = anki('modelFieldNames', modelName=name)['result']
        templates = anki('modelTemplates', modelName=name)['result']
        css = anki('modelStyling', modelName=name)['result']['css']
        print(f'Model: {name}')
        print(f'Fields ({len(fields)}):')
        for i, f in enumerate(fields):
            print(f'  [{i}] {f}')
        print(f'Templates: {list(templates.keys())}')
        print(f'CSS length: {len(css)} chars')
    except Exception as e:
        print(f'Error: {e}')

def add_field(model, field_name):
    """Add a new field to an existing model."""
    # AnkiConnect doesn't have a direct addField API,
    # but updateModelTemplates with new fields works
    fields = anki('modelFieldNames', modelName=model)['result']
    if field_name in fields:
        print(f'Field "{field_name}" already exists.')
        return

    # Get existing templates
    templates = anki('modelTemplates', modelName=model)['result']
    new_fields = fields + [field_name]

    # Rebuild templates with new field
    updated = {}
    for card_name, tmpl in templates.items():
        updated[card_name] = {
            'Front': tmpl['Front'],
            'Back': tmpl['Back']
        }

    anki('updateModelTemplates', model={
        'name': model,
        'templates': updated
    })
    print(f'Added field "{field_name}" to model "{model}".')
    print(f'Fields now: {new_fields}')
    print('Note: Field added but template not updated. Manually add {{' + field_name + '}} to card template in Anki GUI.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        list_models()
        sys.exit(0)

    model = sys.argv[1]

    if '--add' in sys.argv:
        idx = sys.argv.index('--add')
        if idx + 1 < len(sys.argv):
            add_field(model, sys.argv[idx + 1])
        else:
            print('Usage: python anki_model.py MODEL --add FIELD_NAME')
    else:
        show_model(model)
