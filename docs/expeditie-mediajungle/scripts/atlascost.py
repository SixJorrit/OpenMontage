import os, json, urllib.request
from dotenv import load_dotenv
load_dotenv("/Users/jorrit/dev/OpenMontage/.env")
key = os.environ.get("ATLASCLOUD_API_KEY") or os.environ.get("ATLAS_CLOUD_API_KEY")
print("key aanwezig:", bool(key))
def get(path):
    req = urllib.request.Request("https://api.atlascloud.ai" + path,
        headers={"Authorization": f"Bearer {key}", "User-Agent": "curl/8.7.1", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read())
    except Exception as e:
        body = ""
        try: body = e.read()[:400].decode("utf8","replace")
        except Exception: pass
        return {"_error": str(e), "_body": body}
for p in ("/public/v1/balance",
          "/public/v1/model-costs?start_date=2026-08-19&end_date=2026-08-22",
          "/public/v1/model-usage?start_date=2026-08-19&end_date=2026-08-22"):
    print("==", p)
    print(json.dumps(get(p), indent=1)[:2000])
