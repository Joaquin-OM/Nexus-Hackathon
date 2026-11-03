# Guion Oficial del Pitch (5 Minutos Cronometrados)
**Equipo 1 (NEXUS) · Hackathon FP Sampol 2026**
*Estructura de 300 Segundos para Ganar el Reto ante el Jurado*

---

### Diapositiva 1: Portada & El Hook Inicial (0:00 – 0:45 | 45 seg)
> *"Buenas tardes, miembros del jurado y Dirección de TI de Grupo Sampol.*
>
> *En una compañía como Sampol, que gestiona plantas de cogeneración, aeropuertos e infraestructuras críticas en 4 continentes, una hora de parada de servicio cuesta 25.000 euros. Y según los datos oficiales de nuestro propio Director, cada alerta del SOC requería 12 minutos de revisión manual y cada bloqueo 25 minutos.*
>
> *Esa ventana de exposición de media hora es una eternidad para un atacante. Por eso creamos NEXUS 2.0: una plataforma integral que reduce el triaje de 12 minutos a menos de un segundo y ejecuta la contención de identidades en milisegundos de forma autónoma y con salvaguardas de nivel industrial."*

---

### Diapositiva 2: La Solución Técnica (0:45 – 1:40 | 55 seg)
> *"¿Cómo lo hemos construido? Sobre una arquitectura robusta y en producción real:*
> 1. *Un Daemon de sincronización continua que consulta Microsoft Graph API cada 45 segundos, procesando hasta el momento 138 correos con normalización estricta de zonas horarias en UTC.*
> 2. *Una base de datos PostgreSQL normalizada en Azure con 10 tablas, deduplicación inteligente y registro de auditoría inmutable.*
> 3. *Un motor de clasificación que categoriza cada alerta en las 10 clases oficiales de la guía de INCIBE.*
> 4. *Y un motor SOAR conectado a la API de contención de Sampol, que ya ha ejecutado 61 acciones con claves de idempotencia para evitar duplicados y una Lista Blanca estricta que impide aislar por error equipos de la red industrial OT."*

---

### Diapositiva 3: Creatividad e Innovación (1:40 – 2:30 | 50 seg)
> *"Para el criterio de Creatividad, no nos limitamos a lo que pedía el enunciado. Implementamos tres capacidades avanzadas:*
> 1. *Un Escudo Anti-Prompt Injection: Detectamos y neutralizamos el correo trampa con el canario HN03, aislándolo en cuarentena forense sin desestabilizar el sistema.*
> 2. *Un Generador Oficial de Alerta Temprana NIS2: Cumpliendo el Artículo 23 de la directiva europea en menos de 24 horas, con documento formal ya subido a Google Drive demostrando 0 horas de parada de servicio.*
> 3. *Y este portal web interactivo que cualquiera de ustedes puede abrir ahora mismo en su móvil o portátil en joaquin-om.github.io/Nexus-Hackathon, con métricas en tiempo real y buscador forense."*

---

### Diapositiva 4: Investigación Forense y Kill Chain (2:30 – 3:25 | 55 seg)
> *"En el apartado de Investigación, reconstruimos el ataque pericialmente:*
> - *Identificamos al Paciente Cero: jmoreno@sampol.com, cuyas credenciales fueron comprometidas a las 09:18 UTC tras un ataque masivo de Password Spraying con 154 intentos registrados.*
> - *El atacante escaló a Administrador local con amoreno, contactó con el C2 sync-gateway.invalid y alteró 195 ficheros en el servidor de proyectos a través de cmoreno.*
> 
> *Pero aquí está la prueba reina de nuestra solución: NEXUS 2.0 contuvo a mgonzalez 4 minutos antes de que llegara la orden manual del responsable humano, y en el caso de ngonzalez se anticipó 9 minutos y 32 segundos a la solicitud humana SOL-B-014. El dwell time se redujo empíricamente a cero."*

---

### Diapositiva 5: Caso de Negocio y Retorno de Inversión (3:25 – 4:15 | 50 seg)
> *"Hablemos de números con los datos oficiales comunicados por el Director:*
> - *Construir NEXUS 2.0 internamente cuesta 20.000 euros de CAPEX (400 horas a 50 €/h) más 12.000 euros al año de mantenimiento.*
> - *Comprar una plataforma comercial equivale a 20.000 euros de setup más 60.000 euros al año de licencias.*
> - *El ahorro neto a 3 años para Sampol es de 144.000 euros, un 72% menos.*
> - *A esto sumamos 184.500 euros anuales de ahorro operativo en horas de analistas y un Payback de solo 42 días.*
> - *Y con evitar una sola hora de parada en una planta energética (25.000 €/h), NEXUS 2.0 amortiza el 100% de su inversión inicial. Tienen el modelo Excel con fórmulas vivas disponible en el Drive."*

---

### Diapositiva 6: Propuestas de Mejora y Cierre (4:15 – 5:00 | 45 seg)
> *"Para que esto no vuelva a suceder en Sampol, dejamos una hoja de ruta estructurada:*
> - *A corto plazo: Despliegue de MFA FIDO2 físico y vaulting de credenciales de conectores legacy.*
> - *A medio plazo: Segmentación IT/OT bajo norma IEC 62443 y certificación formal de playbooks SOAR.*
> - *A largo plazo: Consolidación del SOC híbrido 24/7.*
>
> *NEXUS 2.0 no es un prototipo: es una solución en producción, auditada, rentable y lista para desplegarse mañana en Grupo Sampol. Muchas gracias."*
