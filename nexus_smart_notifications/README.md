# NEXUS Smart Notifications - modulo integrable

Esta entrega NO modifica el repositorio remoto. Es un complemento para integrar en la version actual de NEXUS SOC.

## Frontend GitHub Pages

1. Copia `frontend/nexus-notifications.css` y `frontend/nexus-notifications.js` a la raiz del repositorio (o ajusta rutas).
2. Antes de `</head>` de `index.html`, inserta `<link rel="stylesheet" href="./nexus-notifications.css">`.
3. Antes de `</body>` inserta:

```html
<script>window.NEXUS_NOTIFICATIONS = { demo: true };</script>
<script src="./nexus-notifications.js" defer></script>
```

4. Publica GitHub Pages. La campana aparece arriba a la derecha. En modo demo, reconocer avisos guarda el estado en localStorage de ese navegador.

## Backend FastAPI (prototipo)

Copia `backend/smart_notifications.py` junto a `backend_api.py` y añade en `backend_api.py` tras crear `app`:

```python
from smart_notifications import router as smart_notifications_router
app.include_router(smart_notifications_router)
```

Ejecuta FastAPI como ya indica el README original. Para probar el endpoint `/api/smart-notifications/evaluate`, usa Swagger (`/docs`) con un incidente ficticio. **NO EXPONGAS ESTE ROUTER A INTERNET SIN AUTENTICACION**. Almacena los eventos en PostgreSQL antes de desplegarlo: el diccionario en memoria se pierde al reiniciar y no sirve para multiples procesos.

Para conectar el frontend a la API, sustituye `demo: true` por `demo: false, apiBase: 'https://TU-BACKEND-HTTPS'` y configura CORS, cookies, autenticacion y autorizacion de usuarios en el backend. Nunca publiques tokens en GitHub Pages.

## Limites y siguientes pasos

- Este modulo no esta conectado a Outlook, n8n, `soar_actions` ni a la base de datos real.
- El motor `evaluate` agrupa por `incident_id` y no decide por si solo si dos alertas pertenecen al mismo incidente.
- La politica P1/P2 es un ejemplo y requiere validacion con TI.
- Antes de produccion: persistencia PostgreSQL, asignacion de destinatarios, turnos, control de permisos, cola de eventos, limites de frecuencia, auditoria y pruebas de carga.
- Para notificaciones del sistema con la web cerrada: HTTPS + PWA + service worker + Web Push.
- Con 200.000 eventos al dia, el backend debe procesar por lotes o colas y notificar incidentes, no eventos individuales.
