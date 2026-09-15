"""Shopify Admin API helper (client-credentials app "Mediajungle content").
Credentials: SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET in ~/.zshrc.local (source it first)."""
import os, json, sys, time, urllib.request, urllib.parse
SHOP = "mediajungle-3848.myshopify.com"
THEME = "gid://shopify/OnlineStoreTheme/157576986955"
API = "2025-07"
def token():
    p = os.path.expanduser('~/.cache/shopify_tok.json')
    if os.path.exists(p):
        d = json.load(open(p))
        if d['exp'] > time.time() + 600: return d['t']
    data = urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': os.environ['SHOPIFY_CLIENT_ID'],
                                   'client_secret': os.environ['SHOPIFY_CLIENT_SECRET']}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(f'https://{SHOP}/admin/oauth/access_token', data=data)))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({'t': r['access_token'], 'exp': time.time() + r['expires_in']}, open(p, 'w')); os.chmod(p, 0o600)
    return r['access_token']
def gql(q, variables=None):
    req = urllib.request.Request(f'https://{SHOP}/admin/api/{API}/graphql.json',
        data=json.dumps({'query': q, 'variables': variables or {}}).encode(),
        headers={'X-Shopify-Access-Token': token(), 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req))
    if d.get('errors'): raise SystemExit(json.dumps(d['errors'], indent=1))
    return d['data']
def files(names):
    d = gql('query($id:ID!,$f:[String!]){theme(id:$id){files(filenames:$f,first:50){nodes{filename body{... on OnlineStoreThemeFileBodyText{content}}}}}}', {'id': THEME, 'f': names})
    return {n['filename']: n['body'].get('content') for n in d['theme']['files']['nodes']}
if __name__ == '__main__':
    if sys.argv[1] == 'get':
        for k, v in files(sys.argv[2:]).items(): print(f'===== {k}\n{v}')
