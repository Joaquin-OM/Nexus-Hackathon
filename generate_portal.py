import json

def main():
    with open('data_export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    html_content = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NEXUS 2.0 — Centro de Operaciones SOC & Respuesta a Incidentes | Equipo 1</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            cyber: {{ bg: '#0b0f19', card: '#111827', border: '#1f2937', accent: '#00f2fe' }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    .glass {{ background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
    .tab-btn.active {{ border-bottom: 2px solid #38bdf8; color: #38bdf8; }}
  </style>
</head>
<body class="text-slate-200 antialiased min-h-screen flex flex-col">

  <!-- HEADER -->
  <header class="border-b border-cyber-border bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap justify-between items-center gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white font-bold text-lg">
          N
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-lg font-bold text-white tracking-tight">NEXUS 2.0</h1>
            <span class="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-950 text-cyan-300 border border-cyan-800">Equipo 1</span>
            <span class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-950 text-emerald-300 border border-emerald-800">Hackathon Sampol 24h</span>
          </div>
          <p class="text-xs text-slate-400">Plataforma de Triaje INCIBE, Contención SOAR y Retorno de Inversión (ROI)</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2 text-xs">
        <div class="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center space-x-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-slate-400">PostgreSQL Azure:</span>
          <span class="font-bold text-white">alertas-soc-1</span>
        </div>
        <div class="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center space-x-1.5">
          <span class="text-slate-400">Alertas Únicas:</span>
          <span class="font-bold text-cyan-400">78</span>
        </div>
        <div class="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center space-x-1.5">
          <span class="text-slate-400">Directriz 1 SOAR:</span>
          <span class="font-bold text-purple-400">22 Bloqueos</span>
        </div>
      </div>
    </div>

    <!-- TABS NAV -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-6 overflow-x-auto text-sm font-medium border-t border-slate-800/60">
      <button onclick="switchTab('tab-resumen')" id="btn-tab-resumen" class="tab-btn active py-3 text-slate-300 hover:text-white transition">📊 1. Resumen Ejecutivo</button>
      <button onclick="switchTab('tab-forense')" id="btn-tab-forense" class="tab-btn py-3 text-slate-400 hover:text-white transition">🕵️ 2. Investigación Forense & Cadenas</button>
      <button onclick="switchTab('tab-soar')" id="btn-tab-soar" class="tab-btn py-3 text-slate-400 hover:text-white transition">⚡ 3. SOAR & Directriz 1 (18:00)</button>
      <button onclick="switchTab('tab-roi')" id="btn-tab-roi" class="tab-btn py-3 text-slate-400 hover:text-white transition">💶 4. Calculadora ROI (Director TI)</button>
      <button onclick="switchTab('tab-directrices')" id="btn-tab-directrices" class="tab-btn py-3 text-slate-400 hover:text-white transition">🎯 5. Directrices Oficiales</button>
      <button onclick="switchTab('tab-dataset')" id="btn-tab-dataset" class="tab-btn py-3 text-slate-400 hover:text-white transition">🗄️ 6. Explorador de Alertas (78)</button>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">

    <!-- TAB 1: RESUMEN EJECUTIVO -->
    <section id="tab-resumen" class="tab-content space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="glass p-5 rounded-xl border border-slate-800">
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Correos Brutos en Buzón</div>
          <div class="text-3xl font-extrabold text-white mt-1">121</div>
          <p class="text-xs text-slate-400 mt-2">Sincronizados vía Microsoft Graph API con hash SHA-256 inmutable.</p>
        </div>
        <div class="glass p-5 rounded-xl border border-slate-800">
          <div class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Alertas Únicas SOC</div>
          <div class="text-3xl font-extrabold text-cyan-400 mt-1">78</div>
          <p class="text-xs text-slate-400 mt-2">Clasificadas bajo las 10 categorías oficiales de la taxonomía INCIBE.</p>
        </div>
        <div class="glass p-5 rounded-xl border border-slate-800">
          <div class="text-xs font-semibold text-amber-400 uppercase tracking-wider">Duplicados y Ruido Filtrado</div>
          <div class="text-3xl font-extrabold text-amber-400 mt-1">30 <span class="text-xs font-normal text-slate-400">(24,8%)</span></div>
          <p class="text-xs text-slate-400 mt-2">21 duplicados/órdenes vinculadas + 9 avisos administrativos descartados.</p>
        </div>
        <div class="glass p-5 rounded-xl border border-slate-800">
          <div class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Ahorro Neto Anual (ROI)</div>
          <div class="text-3xl font-extrabold text-emerald-400 mt-1">281.380 €</div>
          <p class="text-xs text-slate-400 mt-2">Payback en 10 días y ROI del 2.010% frente a costes manuales.</p>
        </div>
      </div>

      <!-- CHARTS -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="glass p-6 rounded-xl border border-slate-800 lg:col-span-2">
          <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4">Distribución de Incidentes por Clase Oficial INCIBE</h3>
          <div class="h-80">
            <canvas id="chartIncibe"></canvas>
          </div>
        </div>
        <div class="glass p-6 rounded-xl border border-slate-800">
          <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4">Severidad Normalizada</h3>
          <div class="h-80">
            <canvas id="chartSev"></canvas>
          </div>
        </div>
      </div>

      <!-- INCIBE SUMMARY TABLE -->
      <div class="glass p-6 rounded-xl border border-slate-800 space-y-4">
        <h3 class="text-base font-bold text-white">Desglose Oficial de Taxonomía INCIBE en Sampol</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full text-xs text-left text-slate-300">
            <thead class="bg-slate-800/80 uppercase text-slate-400 text-[10px]">
              <tr>
                <th class="p-3">Clase INCIBE</th>
                <th class="p-3">Alertas</th>
                <th class="p-3">Peligrosidad</th>
                <th class="p-3">Impacto Típico</th>
                <th class="p-3">Reglas de Amenaza Asociadas</th>
              </tr>
            </thead>
            <tbody id="tbl-incibe-classes" class="divide-y divide-slate-800"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 2: INVESTIGACIÓN FORENSE -->
    <section id="tab-forense" class="tab-content hidden space-y-8">
      <div class="glass p-6 rounded-xl border border-slate-800">
        <h2 class="text-lg font-bold text-white mb-2">🕵️ Reconstrucción de la Campaña Dirigida Multi-Etapa (*moreno@sampol.com)</h2>
        <p class="text-xs text-slate-400 mb-6">
          Análisis forense de correlación cruzada entre usuarios con el mismo apellido en distintas sedes, revelando cómo el actor de amenaza avanzó por la Kill Chain de MITRE ATT&CK.
        </p>

        <div class="space-y-6 relative border-l-2 border-slate-700 ml-4 pl-6">
          <div class="relative">
            <div class="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-red-500 border-4 border-slate-900"></div>
            <div class="text-xs font-semibold text-red-400">1. jmoreno@sampol.com (Sede Barcelona · srv-barcelona-201) — ATAQUE CONSUMADO</div>
            <p class="text-xs text-slate-300 mt-1">
              <strong>AL-0025</strong> (PHISH-LAB) → <strong>AL-0026</strong> (SPRAY-LAB) → <strong>AL-0027</strong> (ACCOUNT-LAB: Acceso ilegítimo) → <strong>AL-0028</strong> (READ-LAB) → <strong>AL-0029</strong> (C2-LAB) → <strong>AL-0030</strong> (MODIFY-LAB: <strong>115 ficheros de proyecto alterados</strong>).
            </p>
          </div>

          <div class="relative">
            <div class="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-red-500 border-4 border-slate-900"></div>
            <div class="text-xs font-semibold text-red-400">2. amoreno@sampol.com (Sede Sevilla · pc-sevilla-202) — ATAQUE CONSUMADO</div>
            <p class="text-xs text-slate-300 mt-1">
              <strong>AL-0032</strong> (EXPLOIT-LAB) → <strong>AL-0033</strong> (APP-LAB: Ejecución remota de comandos) → <strong>AL-0034</strong> (C2-LAB) → <strong>AL-0035</strong> (READ-LAB) → <strong>AL-0036</strong> (MODIFY-LAB: <strong>80 ficheros de proyecto alterados</strong>).
            </p>
          </div>

          <div class="relative">
            <div class="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-emerald-500 border-4 border-slate-900"></div>
            <div class="text-xs font-semibold text-emerald-400">3. cmoreno@sampol.com (Sede Valencia · app-valencia-203) — ¡CONTENIDO POR NEXUS 2.0!</div>
            <p class="text-xs text-slate-300 mt-1">
              <strong>AL-0037</strong> (PHISH-LAB) → <strong>AL-0038</strong> (ACCOUNT-LAB) → <strong>AL-0039</strong> (MALWARE-LAB) → <strong>AL-0040</strong> (C2-LAB) → <span class="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-700">BLOQUEO AUTÓNOMO SOAR</span>. La contención inmediata impidió que el atacante completara la fase de modificación masiva de datos.
            </p>
          </div>

          <div class="relative">
            <div class="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-cyan-500 border-4 border-slate-900"></div>
            <div class="text-xs font-semibold text-cyan-400">4. bmoreno@sampol.com (Sede Bilbao · gw-bilbao-204) — FASE DE ACCESO INICIAL</div>
            <p class="text-xs text-slate-300 mt-1">
              <strong>AL-0043</strong> (PHISH-LAB) → <strong>AL-0044</strong> (SPRAY-LAB: 154 intentos fallidos sin sesión). El motor protegió la cuenta de bloqueo prematuro por no existir sesión comprometida.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: SOAR & DIRECTRIZ 1 -->
    <section id="tab-soar" class="tab-content hidden space-y-8">
      <div class="glass p-6 rounded-xl border border-slate-800">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-bold text-white">⚡ Orquestación SOAR & Playbook Autónomo (Directriz 1)</h2>
            <p class="text-xs text-slate-400">Ejecución automatizada conforme al mandato de las 18:02 CET del Director de TI para bloquear cuentas ante compromiso efectivo.</p>
          </div>
          <span class="px-3 py-1 rounded bg-purple-950 text-purple-300 border border-purple-800 text-xs font-bold">trigger_mode = 'automatico_directriz_1'</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div class="text-xs font-bold text-purple-400">13 Cuentas Comprometidas</div>
            <div class="text-xs text-slate-300 mt-1">Contención autónoma ejecutada en SOAR ante robo de credenciales, intrusión o C2.</div>
          </div>
          <div class="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div class="text-xs font-bold text-cyan-400">3 Falsos Positivos Liberados</div>
            <div class="text-xs text-slate-300 mt-1">Órdenes SOL-L-001, 004 y 007 respetadas; usuarios protegidos de bloqueo erróneo.</div>
          </div>
          <div class="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div class="text-xs font-bold text-emerald-400">Lista Blanca IT/OT Activa</div>
            <div class="text-xs text-slate-300 mt-1">Cuentas directivas (dirti@sampol.com) y servicios críticos protegidos ante bloqueos accidentales.</div>
          </div>
        </div>

        <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-3">Historial de Acciones SOAR en PostgreSQL</h3>
        <div class="overflow-x-auto max-h-96">
          <table class="min-w-full text-xs text-left text-slate-300">
            <thead class="bg-slate-800/80 uppercase text-slate-400 text-[10px] sticky top-0">
              <tr>
                <th class="p-2.5">ID</th>
                <th class="p-2.5">Acción</th>
                <th class="p-2.5">Objetivo</th>
                <th class="p-2.5">Modo Disparo</th>
                <th class="p-2.5">Estado</th>
                <th class="p-2.5">Solicitante</th>
                <th class="p-2.5">Motivo Operativo</th>
              </tr>
            </thead>
            <tbody id="tbl-soar-actions" class="divide-y divide-slate-800"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 4: CALCULADORA ROI -->
    <section id="tab-roi" class="tab-content hidden space-y-8">
      <div class="glass p-6 rounded-xl border border-slate-800">
        <h2 class="text-lg font-bold text-white mb-2">💶 Calculadora Interactiva de Retorno de Inversión (Datos Oficiales Director de TI)</h2>
        <p class="text-xs text-slate-400 mb-6">Ajusta los sliders interactivos en tiempo real para simular los ahorros en triaje, contención SOAR y prevención de paradas de planta.</p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Alertas al mes:</span>
                <span id="lbl-vol" class="font-bold text-cyan-400">3.000</span>
              </div>
              <input type="range" id="slider-vol" min="500" max="10000" step="100" value="3000" oninput="calcROI()" class="w-full accent-cyan-400">
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Tiempo manual revisión (min):</span>
                <span id="lbl-tman" class="font-bold text-cyan-400">12 min</span>
              </div>
              <input type="range" id="slider-tman" min="5" max="30" step="1" value="12" oninput="calcROI()" class="w-full accent-cyan-400">
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Coste hora analista (€/h):</span>
                <span id="lbl-cost" class="font-bold text-cyan-400">45 €</span>
              </div>
              <input type="range" id="slider-cost" min="25" max="100" step="5" value="45" oninput="calcROI()" class="w-full accent-cyan-400">
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Bloqueos manuales / mes:</span>
                <span id="lbl-bloq" class="font-bold text-purple-400">120</span>
              </div>
              <input type="range" id="slider-bloq" min="20" max="500" step="10" value="120" oninput="calcROI()" class="w-full accent-purple-400">
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Minutos por bloqueo manual:</span>
                <span id="lbl-tbloq" class="font-bold text-purple-400">25 min</span>
              </div>
              <input type="range" id="slider-tbloq" min="5" max="45" step="1" value="25" oninput="calcROI()" class="w-full accent-purple-400">
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300">Hora desarrollo interno (€/h):</span>
                <span id="lbl-cdev" class="font-bold text-purple-400">50 €</span>
              </div>
              <input type="range" id="slider-cdev" min="30" max="100" step="5" value="50" oninput="calcROI()" class="w-full accent-purple-400">
            </div>
          </div>

          <div class="p-5 rounded-xl bg-slate-900 border border-slate-700 flex flex-col justify-between">
            <div>
              <div class="text-xs uppercase text-slate-400 font-bold tracking-wider">Ahorro Neto Anual (Build)</div>
              <div id="res-ahorro-neto" class="text-2xl font-black text-emerald-400 mt-1">281.380 €</div>
              <div class="text-xs text-slate-400 mt-2">Payback Estimado: <strong id="res-payback" class="text-white">10 días (0,33 meses)</strong></div>
              <div class="text-xs text-slate-400">ROI Año 1: <strong id="res-roi" class="text-cyan-400">2.010 %</strong></div>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-300">
              <strong>Ventaja vs. Comercial:</strong> Ahorro de <span class="text-emerald-400 font-bold">174.000 € en 3 años</span> frente a la alternativa de mercado (60.000 €/año + 20.000 €).
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 5: DIRECTRICES -->
    <section id="tab-directrices" class="tab-content hidden space-y-8">
      <div class="glass p-6 rounded-xl border border-slate-800">
        <h2 class="text-lg font-bold text-white mb-2">🎯 Trazabilidad de Directrices Oficiales (`dirti@sampol.com`)</h2>
        <p class="text-xs text-slate-400 mb-6">Registro histórico de los requerimientos formales emitidos por la Dirección de TI durante el transcurso del reto y su resolución técnica.</p>

        <div id="cards-directives" class="space-y-4"></div>
      </div>
    </section>

    <!-- TAB 6: DATASET SOC -->
    <section id="tab-dataset" class="tab-content hidden space-y-8">
      <div class="glass p-6 rounded-xl border border-slate-800">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <div>
            <h2 class="text-lg font-bold text-white">🗄️ Explorador de Incidentes Únicos del SOC (78 Alertas)</h2>
            <p class="text-xs text-slate-400">Búsqueda y filtrado en vivo de las alertas almacenadas en Azure PostgreSQL.</p>
          </div>
          <div class="flex items-center gap-2">
            <input type="text" id="search-input" oninput="renderAlertsTable()" placeholder="Buscar usuario, host, regla..." class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-400">
            <select id="filter-class" onchange="renderAlertsTable()" class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-400">
              <option value="">Todas las Clases INCIBE</option>
            </select>
          </div>
        </div>

        <div class="overflow-x-auto max-h-[500px]">
          <table class="min-w-full text-xs text-left text-slate-300">
            <thead class="bg-slate-800/90 uppercase text-slate-400 text-[10px] sticky top-0">
              <tr>
                <th class="p-2.5">Código</th>
                <th class="p-2.5">Fecha (UTC)</th>
                <th class="p-2.5">Severidad</th>
                <th class="p-2.5">Clase INCIBE</th>
                <th class="p-2.5">Usuario</th>
                <th class="p-2.5">Sede</th>
                <th class="p-2.5">Regla / Título</th>
              </tr>
            </thead>
            <tbody id="tbl-alerts" class="divide-y divide-slate-800"></tbody>
          </table>
        </div>
      </div>
    </section>

  </main>

  <!-- FOOTER -->
  <footer class="border-t border-cyber-border bg-slate-950 py-6 mt-auto text-center text-xs text-slate-400">
    <div class="max-w-7xl mx-auto px-4 flex flex-wrap justify-between items-center gap-4">
      <div>
        <strong>NEXUS 2.0</strong> — Diseñado por <strong>Equipo 1</strong> (Joaquín Osés, Sampol Hackathon 24h).
      </div>
      <div class="flex items-center space-x-4">
        <span>PostgreSQL 18.6 Azure</span>
        <span>•</span>
        <span>Microsoft Graph API</span>
        <span>•</span>
        <span>Taxonomía Oficial INCIBE</span>
      </div>
    </div>
  </footer>

  <!-- SCRIPT DATA EMBEDDED -->
  <script>
    const DATA = {json.dumps(data, ensure_ascii=False)};

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.remove('hidden');
      document.getElementById('btn-' + tabId).classList.add('active');
    }}

    // INIT CHARTS
    window.onload = function() {{
      // Bar Chart INCIBE
      const ctxIncibe = document.getElementById('chartIncibe').getContext('2d');
      new Chart(ctxIncibe, {{
        type: 'bar',
        data: {{
          labels: DATA.incibe_distribution.map(d => d.class),
          datasets: [{{
            label: 'Número de Alertas Únicas',
            data: DATA.incibe_distribution.map(d => d.count),
            backgroundColor: '#38bdf8',
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ display: false }} }},
            y: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
          }}
        }}
      }});

      // Doughnut Severidad
      const ctxSev = document.getElementById('chartSev').getContext('2d');
      new Chart(ctxSev, {{
        type: 'doughnut',
        data: {{
          labels: DATA.severity_distribution.map(d => d.severity),
          datasets: [{{
            data: DATA.severity_distribution.map(d => d.count),
            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }} }}
        }}
      }});

      // Render Tables
      renderIncibeTable();
      renderSoarTable();
      renderDirectives();
      populateClassFilter();
      renderAlertsTable();
      calcROI();
    }};

    function renderIncibeTable() {{
      const tbody = document.getElementById('tbl-incibe-classes');
      tbody.innerHTML = DATA.incibe_distribution.map(d => {{
        return `<tr class="hover:bg-slate-800/40">
          <td class="p-3 font-bold text-white">${{d.class}}</td>
          <td class="p-3 text-cyan-400 font-extrabold">${{d.count}}</td>
          <td class="p-3 text-slate-300">Alta / Crítica</td>
          <td class="p-3 text-slate-400">Servicio IT/OT</td>
          <td class="p-3 text-slate-400">Reglas activas del laboratorio Sampol</td>
        </tr>`;
      }}).join('');
    }}

    function renderSoarTable() {{
      const tbody = document.getElementById('tbl-soar-actions');
      tbody.innerHTML = DATA.soar_actions.map(a => {{
        const isAuto = a.trigger_mode.includes('automatico');
        const badgeClass = isAuto ? 'bg-purple-950 text-purple-300 border-purple-800' : 'bg-slate-800 text-slate-300 border-slate-700';
        return `<tr class="hover:bg-slate-800/40">
          <td class="p-2.5 font-mono text-slate-400">#${{a.id}}</td>
          <td class="p-2.5 font-bold ${{a.action === 'bloquear' ? 'text-red-400' : 'text-emerald-400'}}">${{a.action.toUpperCase()}}</td>
          <td class="p-2.5 font-semibold text-white">${{a.target}}</td>
          <td class="p-2.5"><span class="px-2 py-0.5 rounded text-[10px] border ${{badgeClass}}">${{a.trigger_mode}}</span></td>
          <td class="p-2.5 text-slate-300">${{a.status}}</td>
          <td class="p-2.5 text-slate-400">${{a.requested_by}}</td>
          <td class="p-2.5 text-slate-400 truncate max-w-xs" title="${{a.reason}}">${{a.reason}}</td>
        </tr>`;
      }}).join('');
    }}

    function renderDirectives() {{
      const c = document.getElementById('cards-directives');
      c.innerHTML = DATA.directives.map(d => {{
        return `<div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 text-xs font-bold rounded bg-cyan-950 text-cyan-300 border border-cyan-800">Directriz #${{d.num}}</span>
              <strong class="text-white text-sm">${{d.subject}}</strong>
            </div>
            <span class="text-[11px] text-slate-400">${{d.received_at}}</span>
          </div>
          <p class="text-xs text-slate-300 bg-slate-800/50 p-2.5 rounded border border-slate-800"><em>${{d.summary || 'Sin resumen'}}</em></p>
          <div class="text-xs text-emerald-300 font-medium"><strong>Respuesta NEXUS:</strong> ${{d.response || 'Completada'}}</div>
        </div>`;
      }}).join('');
    }}

    function populateClassFilter() {{
      const sel = document.getElementById('filter-class');
      DATA.incibe_distribution.forEach(d => {{
        const opt = document.createElement('option');
        opt.value = d.class;
        opt.textContent = `${{d.class}} (${{d.count}})`;
        sel.appendChild(opt);
      }});
    }}

    function renderAlertsTable() {{
      const q = document.getElementById('search-input').value.toLowerCase();
      const cls = document.getElementById('filter-class').value;
      const tbody = document.getElementById('tbl-alerts');

      const filtered = DATA.alerts.filter(a => {{
        const matchQ = !q || (a.user && a.user.toLowerCase().includes(q)) ||
                              (a.code && a.code.toLowerCase().includes(q)) ||
                              (a.rule && a.rule.toLowerCase().includes(q)) ||
                              (a.title && a.title.toLowerCase().includes(q)) ||
                              (a.sede && a.sede.toLowerCase().includes(q));
        const matchC = !cls || a.class === cls;
        return matchQ && matchC;
      }});

      tbody.innerHTML = filtered.slice(0, 100).map(a => {{
        return `<tr class="hover:bg-slate-800/40">
          <td class="p-2.5 font-mono text-cyan-400 font-bold">${{a.code}}</td>
          <td class="p-2.5 text-slate-400 font-mono text-[10px]">${{a.timestamp.substring(0, 16)}}</td>
          <td class="p-2.5 font-bold ${{a.severity === 'CRITICA' ? 'text-red-400' : 'text-amber-400'}}">${{a.severity}}</td>
          <td class="p-2.5 text-slate-200">${{a.class}}</td>
          <td class="p-2.5 font-medium text-white">${{a.user || '-'}}</td>
          <td class="p-2.5 text-slate-400">${{a.sede || 'No indicada'}}</td>
          <td class="p-2.5 text-slate-300 truncate max-w-sm" title="${{a.justification}}">${{a.rule || a.title}}</td>
        </tr>`;
      }}).join('');
    }}

    function calcROI() {{
      const vol = parseFloat(document.getElementById('slider-vol').value);
      const tman = parseFloat(document.getElementById('slider-tman').value);
      const cost = parseFloat(document.getElementById('slider-cost').value);
      const bloq = parseFloat(document.getElementById('slider-bloq').value);
      const tbloq = parseFloat(document.getElementById('slider-tbloq').value);
      const cdev = parseFloat(document.getElementById('slider-cdev').value);

      document.getElementById('lbl-vol').textContent = vol.toLocaleString();
      document.getElementById('lbl-tman').textContent = tman + ' min';
      document.getElementById('lbl-cost').textContent = cost + ' €';
      document.getElementById('lbl-bloq').textContent = bloq.toLocaleString();
      document.getElementById('lbl-tbloq').textContent = tbloq + ' min';
      document.getElementById('lbl-cdev').textContent = cdev + ' €';

      const hTriajeActual = (vol * tman) / 60.0;
      const cTriajeActual = hTriajeActual * cost;
      const hTriajeNexus = (vol * 2.0) / 60.0;
      const cTriajeNexus = hTriajeNexus * cost;
      const ahTriajeMes = cTriajeActual - cTriajeNexus;

      const hSoarActual = (bloq * tbloq) / 60.0;
      const cSoarActual = hSoarActual * cost;
      const hSoarNexus = (bloq * 1.5) / 60.0;
      const cSoarNexus = hSoarNexus * cost;
      const ahSoarMes = cSoarActual - cSoarNexus;

      const ahBrutoMes = ahTriajeMes + ahSoarMes;
      const ahNetoMes = ahBrutoMes - 500.0;
      const inversionInicial = 160.0 * cdev;
      const payback = inversionInicial / ahNetoMes;
      const costeTotal1y = inversionInicial + (500.0 * 12.0);
      const beneficioAnual = ahBrutoMes * 12.0;
      const roi = ((beneficioAnual - costeTotal1y) / costeTotal1y) * 100.0;

      document.getElementById('res-ahorro-neto').textContent = Math.round(ahNetoMes * 12).toLocaleString() + ' € / año';
      document.getElementById('res-payback').textContent = Math.round(payback * 30) + ' días (' + payback.toFixed(2) + ' meses)';
      document.getElementById('res-roi').textContent = Math.round(roi).toLocaleString() + ' %';
    }}
  </script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print('index.html created successfully!')

if __name__ == '__main__':
    main()
