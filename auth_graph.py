import urllib.request
import urllib.parse
import json
import time
import sys

TENANT_ID = "8723e25f-512e-4b45-ba24-cd2c9a55108e"
# Microsoft Office first-party Client ID (pre-consented for Microsoft Graph Mail.Read in M365)
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
SCOPE = "https://graph.microsoft.com/.default offline_access"
TOKEN_FILE = r"C:\Users\osesj\Documents\Nexus-Hackathon\.graph_token.json"

def main():
    device_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "scope": SCOPE
    }).encode()
    req = urllib.request.Request(device_url, data=data)
    with urllib.request.urlopen(req, timeout=10) as resp:
        device_info = json.loads(resp.read().decode())

    print("=================================================================", flush=True)
    print("CONEXIÓN AL BUZÓN OUTLOOK (equipo_1_hackaton@sampol.com)", flush=True)
    print("1. Abre en el navegador: https://login.microsoft.com/device", flush=True)
    print(f"2. Introduce este código: {device_info['user_code']}", flush=True)
    print("3. Selecciona la cuenta equipo_1_hackaton@sampol.com", flush=True)
    print("=================================================================", flush=True)

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    interval = device_info.get("interval", 5)
    expires_in = device_info.get("expires_in", 900)
    start_time = time.time()

    while time.time() - start_time < expires_in:
        time.sleep(interval)
        poll_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": device_info["device_code"]
        }).encode()
        poll_req = urllib.request.Request(token_url, data=poll_data)
        try:
            with urllib.request.urlopen(poll_req, timeout=10) as t_resp:
                token_data = json.loads(t_resp.read().decode())
                token_data["obtained_at"] = time.time()
                token_data["client_id"] = CLIENT_ID
                token_data["tenant_id"] = TENANT_ID
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    json.dump(token_data, f, indent=2)
                print("¡AUTENTICACIÓN COMPLETADA Y TOKEN GUARDADO!", flush=True)

                # Probar lectura del perfil y conteo de mensajes
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                me_req = urllib.request.Request("https://graph.microsoft.com/v1.0/me/messages?$top=5&$select=id,subject,receivedDateTime,from", headers=headers)
                with urllib.request.urlopen(me_req, timeout=10) as m_resp:
                    msgs = json.loads(m_resp.read().decode())
                    items = msgs.get("value", [])
                    print(f"Conexión verificada: leídos {len(items)} correos recientes de muestra.", flush=True)
                    for m in items:
                        print(" -", m.get("receivedDateTime"), "|", m.get("subject"), flush=True)
                return
        except urllib.error.HTTPError as e:
            err_body = json.loads(e.read().decode())
            err_code = err_body.get("error")
            if err_code == "authorization_pending":
                continue
            elif err_code == "slow_down":
                interval += 5
                continue
            else:
                print("Error en autenticación:", err_body, flush=True)
                sys.exit(1)

if __name__ == "__main__":
    main()
