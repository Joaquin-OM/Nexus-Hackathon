import urllib.request
import urllib.parse
import json
import os
import time

TOKEN_FILE = r"C:\Users\osesj\Documents\Nexus-Hackathon\.graph_token.json"
DUMP_FILE = r"C:\Users\osesj\Documents\Nexus-Hackathon\mailbox_dump.json"

def get_valid_token():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        tdata = json.load(f)
    # Refresh if older than 45 min
    if time.time() - tdata.get("obtained_at", 0) > 2700 and "refresh_token" in tdata:
        token_url = f"https://login.microsoftonline.com/{tdata['tenant_id']}/oauth2/v2.0/token"
        poll_data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": tdata["client_id"],
            "refresh_token": tdata["refresh_token"],
            "scope": "https://graph.microsoft.com/.default offline_access"
        }).encode()
        req = urllib.request.Request(token_url, data=poll_data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            new_t = json.loads(resp.read().decode())
            tdata.update(new_t)
            tdata["obtained_at"] = time.time()
            with open(TOKEN_FILE, "w", encoding="utf-8") as fw:
                json.dump(tdata, fw, indent=2)
    return tdata["access_token"]

def graph_get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.body-content-type="text"'
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def graph_get_html(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}"
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def main():
    token = get_valid_token()
    folders = graph_get("https://graph.microsoft.com/v1.0/me/mailFolders?$top=50", token)
    print("=== CARPETAS DEL BUZÓN ===")
    for fld in folders.get("value", []):
        print(f" - {fld['displayName']} (id={fld['id']}): total={fld.get('totalItemCount')}, unread={fld.get('unreadItemCount')}")

    # Descargar todos los mensajes (paginando)
    all_messages = []
    next_url = "https://graph.microsoft.com/v1.0/me/messages?$top=100&$orderby=receivedDateTime%20asc&$select=id,internetMessageId,conversationId,subject,receivedDateTime,sentDateTime,from,sender,toRecipients,ccRecipients,hasAttachments,importance,bodyPreview,body,internetMessageHeaders,parentFolderId"
    while next_url:
        page = graph_get_html(next_url, token)
        msgs = page.get("value", [])
        all_messages.extend(msgs)
        next_url = page.get("@odata.nextLink")

    print(f"\nTotal mensajes descargados: {len(all_messages)}")

    # Si alguno tiene adjuntos, descargar metadatos/contenido de adjuntos
    for m in all_messages:
        if m.get("hasAttachments"):
            att_url = f"https://graph.microsoft.com/v1.0/me/messages/{m['id']}/attachments"
            try:
                atts = graph_get_html(att_url, token).get("value", [])
                m["attachments_data"] = atts
                print(f"Adjuntos en '{m.get('subject')}': {[a.get('name') for a in atts]}")
            except Exception as e:
                print(f"Error leyendo adjuntos de {m['id']}: {e}")

    with open(DUMP_FILE, "w", encoding="utf-8") as f:
        json.dump(all_messages, f, indent=2, ensure_ascii=False)

    print("\n=== LISTADO DE TODOS LOS CORREOS (ORDEN CRONOLÓGICO) ===")
    for i, m in enumerate(all_messages, 1):
        frm = m.get("from", {}).get("emailAddress", {}).get("address", "")
        print(f"{i:02d}. [{m.get('receivedDateTime')}] De: {frm} | Asunto: {m.get('subject')} | Adjuntos: {m.get('hasAttachments')}")

if __name__ == "__main__":
    main()
