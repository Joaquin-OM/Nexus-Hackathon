import os
import ssl
import pg8000.native

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

def load_dotenv(path=ENV_PATH):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k not in os.environ:
                os.environ[k] = v

load_dotenv()

DB_CONFIG = {
    "user": os.environ.get("PGUSER", "team1"),
    "password": os.environ.get("PGPASSWORD", ""),
    "host": os.environ.get("PGHOST", "alertas-soc-1.postgres.database.azure.com"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "database": os.environ.get("PGDATABASE", "postgres"),
}

SOAR_API_URL = os.environ.get("SOAR_API_URL", "https://hackathon-api-a6ckg4g2ejg4cda4.francecentral-01.azurewebsites.net").rstrip("/")
SOAR_API_KEY = os.environ.get("SOAR_API_KEY", "")
SOAR_TEAM_PREFIX = os.environ.get("SOAR_TEAM_PREFIX", "/equipo-1")
GRAPH_TENANT_ID = os.environ.get("GRAPH_TENANT_ID", "8723e25f-512e-4b45-ba24-cd2c9a55108e")
GRAPH_CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "d3590ed6-52b3-4102-aeff-aad2292ab01c")

def get_conn():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return pg8000.native.Connection(ssl_context=ssl_context, **DB_CONFIG)


import urllib.request
import urllib.error
import json
from typing import Optional, Tuple, Any

def call_sampol_soar_api(endpoint_suffix: str, method: str = "GET", payload: Optional[dict] = None) -> Tuple[int, Any]:
    url = f"{SOAR_API_URL}{SOAR_TEAM_PREFIX}{endpoint_suffix}"
    headers = {"X-API-Key": SOAR_API_KEY, "Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        err_txt = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_txt)
        except Exception:
            err_json = {"error": err_txt}
        return e.code, err_json
    except Exception as e:
        return 500, {"error": str(e)}
