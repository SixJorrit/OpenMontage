"""Upload images/videos to Shopify Files via staged uploads. Usage: python upload.py file1 file2 ..."""
import sys, os, json, mimetypes, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from shop import gql
paths = sys.argv[1:]; inputs = []
for p in paths:
    mt = mimetypes.guess_type(p)[0]; res = 'VIDEO' if mt.startswith('video') else 'IMAGE'
    inputs.append({'filename': os.path.basename(p), 'mimeType': mt, 'resource': res, 'httpMethod': 'POST', 'fileSize': str(os.path.getsize(p))})
d = gql('mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){stagedTargets{url resourceUrl parameters{name value}} userErrors{field message}}}', {'i': inputs})['stagedUploadsCreate']
if d['userErrors']: raise SystemExit(d['userErrors'])
files = []
for p, inp, t in zip(paths, inputs, d['stagedTargets']):
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}']
    for prm in t['parameters']: cmd += ['-F', f"{prm['name']}={prm['value']}"]
    cmd += ['-F', f"file=@{p}", t['url']]
    print('upload', inp['filename'], subprocess.check_output(cmd).decode())
    fc = {'originalSource': t['resourceUrl'], 'contentType': inp['resource'], 'alt': ''}
    if inp['resource'] == 'IMAGE': fc['filename'] = inp['filename']   # video: filename is derived by Shopify
    files.append(fc)
r = gql('mutation($f:[FileCreateInput!]!){fileCreate(files:$f){files{id fileStatus} userErrors{field message}}}', {'f': files})['fileCreate']
print(json.dumps(r, indent=1))
