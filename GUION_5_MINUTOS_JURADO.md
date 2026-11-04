# 🎤 Guion de Presentación Oficial (5 Minutos): NEXUS SOC 2.0 (SAMPOL)

**Audiencia:** Jurado del Hackathon FP SAMPOL y Dirección de TI  
**Estructura:** 5 Bloques alineados al 100% con la Rúbrica Oficial (100% de la Puntuación)  
**URL de la Demo en Vivo:** [https://joaquin-om.github.io/Nexus-Hackathon/?v=5](https://joaquin-om.github.io/Nexus-Hackathon/?v=5)  

---

## ⏱️ Minuto a Minuto de la Exposición

```
[0:00 - 1:00] BLOQUE 1: Solución y Demo en Vivo (Peso: 20%)
[1:00 - 2:00] BLOQUE 2: Investigación y Causa Raíz (Peso: 15%)
[2:00 - 3:00] BLOQUE 3: Análisis de Negocio y Finanzas (Peso: 20%)
[3:00 - 4:00] BLOQUE 4: Creatividad y Defensa Activa (Peso: 30% - Máximo Peso)
[4:00 - 5:00] BLOQUE 5: Propuestas de Mejora para SAMPOL y Cierre (Peso: 15%)
```

---

### [0:00 – 1:00] BLOQUE 1: La Solución y Demostración en Vivo (Rúbrica: 20%)
*(Tener abierta en pantalla la aplicación con el Login corporativo o ya dentro del Dashboard)*

> *"Buenos días a todos, miembros del jurado y Dirección de TI.*
> 
> *Durante estas 24 horas nos hemos enfrentado al reto real que vive SAMPOL: un buzón desbordado por cientos de alertas inconexas, falta de trazabilidad y minutos vitales perdidos mientras un ataque se propaga.*
> 
> *Para resolverlo hemos desarrollado **NEXUS SOC 2.0**: una plataforma integral de triaje forense, clasificación unificada y respuesta autónoma (SOAR).*
> 
> *(Mostrar login o acceder)*: *El sistema cuenta con un control de acceso Zero Trust restringido exclusivamente a cuentas `@sampol.com` con integración de Microsoft 365 SSO.*
> 
> *Hemos conectado y procesado el **100% de los 326 correos del buzón**, normalizando 311 alertas bajo la **taxonomía oficial de 10 clases de INCIBE** y almacenándolas en Azure PostgreSQL con hash SHA-256 para garantizar la cadena de custodia.*
> 
> *(Señalar el Dashboard en vivo)*: *En pantalla el Director ve de un vistazo los KPIs de mando, la distribución cuantitativa por gravedad y el panel operativo de incidentes prioritarios. Y lo más importante: **es operativo**. Si hago clic en 'Gestionar' en esta alerta crítica y pulso 'Ejecutar Contención SOAR' *(hacer clic)*, el sistema aísla el activo y revoca sesiones en milisegundos con trazabilidad total."*

---

### [1:00 – 2:00] BLOQUE 2: Investigación Forense y Kill Chain (Rúbrica: 15%)
*(Navegar brevemente a la sección de Incidentes Prioritarios o Kill Chain)*

> *"Nuestra labor no fue solo clasificar alertas, sino entender la verdad que escondía el buzón. Reconstruimos la Cyber Kill Chain completa y descubrimos un ataque coordinado en 7 fases:*
> 
> 1. ***Paciente Cero y Acceso Inicial:** Identificamos que el origen fue el equipo `LAB-WS-17`, donde un usuario cayó en un correo de phishing dirigido.*
> 2. ***Escalada de Privilegios:** El malware volcó credenciales de memoria LSASS y comprometió la cuenta técnica `ejercicio.backup`, abusando de sus privilegios `SeBackupPrivilege`.*
> 3. ***Movimiento Lateral y Persistencia:** El adversario saltó por SMB (puerto 445) hacia `LAB-APP-04` instalando una tarea programada oculta llamada `System Health Check` y un binario de soporte remoto.*
> 4. ***Exfiltración y Cifrado:** Antes de alertar al SOC, exfiltraron 18 GB mediante `7za.exe` hacia la IP `198.51.100.77` y procedieron al cifrado de `LAB-FS-01` con extensión `.locked`.*
> 
> *Pero el hallazgo pericial más crítico fue **la cortina de humo**: mientras el ransomware colapsaba los servidores, a las 00:51 UTC los atacantes modificaron encubiertamente el IBAN de los proveedores en Finanzas para desviar transferencias masivas. Detectamos la discrepancia a tiempo y congelamos la pasarela de pagos: **pérdida económica = cero euros**.*
> 
> *Además, demostramos que la supuesta filtración pública en el sitio 'BLACK VAULT' era falsa: el dominio `black-vault.invalid` es un dominio reservado sin resolución DNS pública, usado únicamente para presionar psicológicamente a Dirección."*

---

### [2:00 – 3:00] BLOQUE 3: Análisis de Negocio y Finanzas (Rúbrica: 20%)
*(Hacer clic en la pestaña 'Calculadora de ROI' en el menú lateral)*

> *"Toda solución técnica debe sostenerse con números de negocio demostrables. En la pestaña de finanzas hemos modelado el retorno económico:*
> 
> * **Situación Actual sin NEXUS:** Un volumen típico de 500 alertas mensuales revisadas manualmente a 10 minutos por alerta consume 83 horas de analista al mes. A 30 €/hora, SAMPOL gasta 2.500 € mensuales solo en triaje manual repetitivo.*
> * **Con NEXUS SOC 2.0:** El triaje automatizado reduce el tiempo de revisión a sub-segundos. Con nuestras 80 acciones de bloqueo SOAR autónomo, ahorramos más de 50 horas de trabajo cualificado al mes: **un ahorro neto de más de 15.000 € anuales**.*
> * **Coste Evitado (Risk Avoidance):** Detener la transferencia fraudulenta en Finanzas y contener los 18 GB de datos evita sanciones de hasta el 4% de facturación por RGPD/NIS2 y costes de extorsión de más de 100.000 €.*
> * **Amortización:** Con una inversión inicial de desarrollo estimada en 20.000 €, **el periodo de recuperación (Payback) es inferior a 2 meses** y el **ROI del primer año supera el 140%**."*

---

### [3:00 – 4:00] BLOQUE 4: Creatividad y Defensa Activa (Rúbrica: 30% - Criterio Clave)
> *"El jurado busca ideas que nadie nos pidió y que el Director querría tener funcionando mañana mismo. Para Grupo SAMPOL hemos diseñado tres innovaciones de defensa activa:*
> 
> 1. **Carpetas Cebo con 'Canary Traps' Anti-Ransomware:**  
>    *Creamos carpetas trampa invisibles (`!00_Admin_Canary`) con ficheros cebo vigilados por un micro-sensor de kernel. Si cualquier proceso desconocido intenta tocar o renombrar un archivo canario, el sistema mata el proceso y corta la interfaz de red en menos de 50 milisegundos. El ransomware muere antes de cifrar un solo documento legítimo.*
> 
> 2. **Honeytokens en Active Directory con Auto-Aislamiento:**  
>    *Desplegamos cuentas señuelo como `admin-backup-sampol` con contraseñas accesibles y SPNs configurados. Un usuario real jamás las usa; si un atacante intenta hacer password spraying o Kerberoasting contra esa cuenta, el SOAR aísla su IP perimetral automáticamente con **cero falsos positivos**.*
> 
> 3. **Zero-Trust Banking (Regla de 4 Ojos con Token Físico):**  
>    *Para blindar a Finanzas ante suplantaciones (BEC) y llamadas de vishing como las del simulacro, establecemos que cualquier modificación de cuenta bancaria o pago superior a 5.000 € requiere la firma criptográfica en hardware físico (FIDO2) de dos directivos independientes. Se acaba el fraude por correo de raíz."*

---

### [4:00 – 5:00] BLOQUE 5: Propuestas de Mejora Estructurales para SAMPOL y Cierre (Rúbrica: 15%)
> *"A partir de lo descubierto en el incidente, nuestras cuatro propuestas estratégicas para SAMPOL son:*
> 
> 1. **Desacoplamiento IT/OT (Norma IEC 62443):**  
>    *SAMPOL opera infraestructuras críticas: aeropuertos, plantas de cogeneración y microrredes energéticas. Debemos aislar las redes SCADA con cortafuegos industriales y zonas desmilitarizadas para que un ransomware corporativo jamás detenga una planta energética ni un aeropuerto.*
> 2. **Microsegmentación Zero-Trust Endpoint:**  
>    *Prohibir por política de firewall local cualquier conexión directa entre puestos de trabajo por puerto 445 (SMB) y 3389 (RDP). Si un usuario cae por phishing, el atacante queda atrapado en esa máquina y no puede propagarse.*
> 3. **Cuentas de Servicio Administradas gMSA:**  
>    *Eliminar cuentas de backup con contraseñas estáticas; Active Directory debe rotar claves de 128 caracteres automáticamente cada pocos días.*
> 4. **Cyber Range y Gemelo Digital OT:**  
>    *Crear un entorno virtual de simulación para entrenar conjuntamente a los operadores de planta y al equipo de TI ante ataques híbridos.*
> 
> *En conclusión: NEXUS SOC 2.0 no es un proyecto de laboratorio, es una plataforma operativa que convierte la fatiga de alertas en contención autónoma y protege el negocio de SAMPOL.*
> 
> *Muchas gracias, quedamos a disposición del jurado para sus preguntas."*

---

## 🎯 Consejos para los 3 Minutos de Preguntas del Jurado

- **Si preguntan: "¿Por qué elegisteis phishing y no soporte remoto como causa inicial?"**  
  *Respuesta:* "Porque las evidencias demuestran que el puesto `LAB-WS-17` no tenía sesiones RMM activas a la hora de la intrusión; el software RMM y la tarea programada se crearon en una fase posterior en `LAB-APP-04` como mecanismo de persistencia secundario tras el robo de credenciales."
- **Si preguntan: "¿Cómo garantizáis que el SOAR no bloquee a un usuario legítimo?"**  
  *Respuesta:* "El motor es idempotente y valida órdenes de liberación previas (Directriz 5). Además, solo bloquea ante eventos confirmados de compromiso (como ráfagas de autenticación anómala multi-sede o modificación masiva) y cuenta con lista blanca para personal crítico."
- **Si preguntan: "¿Qué fue de los 18 GB exfiltrados?"**  
  *Respuesta:* "Fueron bloqueados a nivel perimetral cortando la IP `198.51.100.77`. Correlacionamos los logs MFT/USN Journal para determinar el alcance exacto y cumplir el plazo legal de notificación de 72 horas ante la AEPD y el DPD."
