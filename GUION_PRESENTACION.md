# 🎤 Guion de Presentación: NEXUS SOC 2.0 (SAMPOL)

**Duración:** 2:30 – 3:00 minutos  
**Audiencia:** Jurado del Hackathon, Dirección de TI y Responsables de Ciberseguridad / Operaciones  
**URL de la Demo en Vivo:** [https://joaquin-om.github.io/Nexus-Hackathon/?v=3](https://joaquin-om.github.io/Nexus-Hackathon/?v=3)  

---

## ⏱️ Minuto a Minuto de la Presentación

### 1. El Problema y la Solución (0:00 – 0:35)
> *"Buenos días a todos.*
> 
> *En un Centro de Operaciones de Seguridad real, el mayor enemigo de los analistas no son solo los ciberataques, sino la **fatiga de alertas**: cientos de eventos inconexos entrando por minuto, falta de contexto pericial y minutos vitales perdidos mientras un ransomware se expande en la red corporativa.*
> 
> *Para resolver esto hemos creado **NEXUS SOC 2.0**, una plataforma unificada de triaje pericial, correlación de incidentes y respuesta autónoma (SOAR) diseñada específicamente para la infraestructura crítica y corporativa de SAMPOL."*

---

### 2. Cómo Funciona y Demostración en Vivo (0:35 – 1:35)
*(Tener abierta la pantalla principal de la aplicación)*

> *"¿Cómo funciona nuestro flujo de datos? Nuestro motor ingiere los eventos de telemetría de todos los sensores y buzones, los procesa y normaliza bajo la **taxonomía oficial de INCIBE** en diez categorías maestras, y los presenta en tres niveles operativos en la pantalla principal:*
> 
> 1. **Valores Principales (Cabecera):** *(Señalar los KPIs superiores)* De un solo vistazo, Dirección y Guardia conocen el estado en vivo: alertas totales ingeridas, alertas críticas P1 bajo SLA estricto, mitigaciones SOAR y una **reducción de ruido del 65%**.
> 2. **Distribución Cuantitativa por Gravedad:** *(Señalar el gráfico central)* Visualizamos el volumen exacto clasificado por criticidad. Además, es totalmente interactivo: con un clic en las tarjetas de 'Crítica' o 'Alta', toda la consola inferior se filtra en tiempo real.
> 3. **Panel Operativo de Gestión y Triaje:** *(Bajar a la tabla y hacer clic en el botón 'Gestionar' de una alerta crítica)* El analista no pierde tiempo saltando entre herramientas. Abre el detalle forense de la alerta, evalúa el host, usuario o IP afectado y, con un solo clic en **'Ejecutar Contención SOAR'**, aísla el activo en el EDR o bloquea la IP en el firewall perimetral con trazabilidad inmediata."*

---

### 3. Capacidades Clave Implementadas (1:35 – 2:15)
*(Navegar brevemente por las pestañas del menú lateral si se desea ilustrar)*

> *"Además del triaje en tiempo real, la plataforma incorpora tres pilares de valor diferencial:*
> 
> * **Control estricto de SLAs (Directivas de Dirección de TI):** Alertas P1 con acuse garantizado en menos de 10 minutos y respuesta técnica en menos de 20 minutos, respaldado por un sistema de notificaciones prioritarias.
> * **Cadena de Custodia y Auditoría Forense:** Registro inmutable de eventos con correlación MITRE ATT&CK, trazabilidad RFC 822 y preparación técnica para cumplir con la notificación a DPD / AEPD en la ventana de 72 horas.
> * **Calculadora de Retorno y Finanzas (ROI):** Un módulo que traduce los minutos de triaje ahorrados por analista en ahorro económico directo y retorno medible para el negocio."*

---

### 4. Áreas de Crecimiento en Entorno Real para SAMPOL (2:15 – 3:00)
> *"Si esta solución se implantase mañana en producción dentro del grupo SAMPOL, sus tres vías naturales de evolución son:*
> 
> 1. **Supervisión de Entornos Industriales y OT:** Conectar los sensores con los PLCs y sistemas SCADA de aeropuertos, plantas de cogeneración, redes de distribución y microrredes que opera SAMPOL, protegiendo infraestructuras críticas que no admiten paradas.
> 2. **Integración API Bidireccional con EDRs y Firewalls Corporativos:** Conectar el motor SOAR de forma nativa a Microsoft Sentinel, CrowdStrike, Palo Alto o Fortinet para que las órdenes de bloqueo se propaguen a nivel global en segundos.
> 3. **Asistente de IA para Informes Regulatorios NIS2 y RGPD:** Automatizar la redacción pericial preliminar requerida por INCIBE-CERT y la Agencia Española de Protección de Datos ante brechas de seguridad confirmadas.
> 
> *En conclusión: NEXUS transforma el ruido masivo en decisiones operativas y permite contener un incidente antes de que se convierta en una catástrofe de negocio. Muchas gracias."*

---

## 🎯 Consejos Prácticos para la Exposición

1. **Interacción en Directo:**  
   En el minuto 1:15, pulsa el botón **"Gestionar"** en la alerta crítica `SOC-20261103-007` y pulsa **"Ejecutar Contención SOAR (Aislar / Bloquear)"**. Aparecerá el aviso toast verde de éxito y el estado cambiará a *Contenido SOAR*. Causa un impacto visual inmediato.
2. **Respaldo con Datos del Simulacro:**  
   Menciona que durante la madrugada se gestionó un simulacro real de 15 hitos críticos (ransomware, exfiltración, tampering de backups) con **100% de cumplimiento de SLA**.
3. **Cache-Buster del Enlace:**  
   Si en algún proyector se ve la versión anterior en caché, usa la URL con parámetro de versión: `https://joaquin-om.github.io/Nexus-Hackathon/?v=3`.
