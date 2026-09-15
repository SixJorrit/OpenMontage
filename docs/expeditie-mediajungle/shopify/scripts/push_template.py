"""Publish ../page.expeditie-mediajungle.json to templates/page.expeditie-mediajungle.json in the live theme."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from shop import gql, THEME
here = os.path.dirname(os.path.abspath(__file__))
new = open(os.path.join(here, '..', 'page.expeditie-mediajungle.json')).read()
json.loads(new)  # validate
r = gql('mutation($id:ID!,$f:[OnlineStoreThemeFilesUpsertFileInput!]!){themeFilesUpsert(themeId:$id,files:$f){upsertedThemeFiles{filename} userErrors{filename code message}}}',
        {'id': THEME, 'f': [{'filename': 'templates/page.expeditie-mediajungle.json', 'body': {'type': 'TEXT', 'value': new}}]})
print(json.dumps(r, indent=1, ensure_ascii=False))
