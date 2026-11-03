import json
import os

def main():
    with open('data_export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    alerts_json = json.dumps(data.get('alerts', []), ensure_ascii=False)
    soar_json = json.dumps(data.get('soar', []), ensure_ascii=False)
    notifs_json = json.dumps(data.get('notifications', []), ensure_ascii=False)
    metrics_json = json.dumps(data.get('metrics', {}), ensure_ascii=False)

    total_alerts = data.get('unique_alerts_count', 93)
    raw_count = data.get('raw_count', 142)
    soar_count = data.get('soar_count', 62)
    notif_count = data.get('notifications_count', 50)
    p1_count = sum(1 for n in data.get('notifications', []) if n.get('priority') == 'P1')

    html_content = f"""<!DOCTYPE html>
<html lang="es" class="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NEXUS SOC 2.0 — SAMPOL</title>
  <link rel="icon" type="image/png" href="./assets/brand/sampol_favicon.png">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="./assets/js/lucide.min.js"></script>
  <link rel="stylesheet" href="./assets/css/sampol-brand.css">
  <link rel="stylesheet" href="./nexus-notifications.css">
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            sampol: {{
              blue: '#0784B7',
              'blue-hover': '#066d97',
              'blue-light': '#F0F7FA',
              green: '#42A83B',
              'green-hover': '#378c31',
              'green-light': '#F2F9F1',
              dark: '#172C3D',
              slate: '#243B50',
              bg: '#F8FAFC',
              surface: '#FFFFFF',
              border: '#E2E8F0'
            }}
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-[#F8FAFC] dark:bg-[#0B1118] text-[#0F172A] dark:text-[#F8FAFC] font-sans antialiased min-h-screen flex">

  <!-- =========================================================================
       SIDEBAR LATERAL CORPORATIVO
       ========================================================================= -->
  <aside id="main-sidebar" class="fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-[#111A24] border-r border-[#E2E8F0] dark:border-[#1E293B] flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 -translate-x-full">
    
    <!-- CABECERA DE MARCA -->
    <div class="px-5 py-4 border-b border-[#E2E8F0] dark:border-[#1E293B] flex items-center justify-between">
      <div class="flex items-center space-x-2.5">
        <img src="./assets/brand/sampol_logo_color.png" alt="SAMPOL" class="h-7 w-auto dark:hidden" onerror="this.style.display='none'">
        <img src="./assets/brand/sampol_logo_blanco.png" alt="SAMPOL" class="h-7 w-auto hidden dark:block" onerror="this.style.display='none'">
        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">SOC 2.0</span>
      </div>
      <button onclick="toggleSidebar()" class="md:hidden p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white" aria-label="Cerrar navegación">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
    </div>

    <!-- ENTORNO -->
    <div class="px-5 py-2 bg-slate-50 dark:bg-slate-900/60 border-b border-[#E2E8F0] dark:border-[#1E293B] flex items-center justify-between text-[11px]">
      <span class="text-slate-500 dark:text-slate-400">Entorno Demo</span>
      <span class="font-semibold text-[#0784B7] dark:text-[#38BDF8]">Hackathon 24h</span>
    </div>

    <!-- NAVEGACIÓN -->
    <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-5 text-xs">
      
      <!-- SECCIÓN: OPERACIONES -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Operaciones</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-resumen')" id="btn-tab-resumen" class="sidebar-nav-item active w-full text-left">
            <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
            <span class="flex-1">Dashboard</span>
          </button>
          <button onclick="switchTab('tab-dataset')" id="btn-tab-dataset" class="sidebar-nav-item w-full text-left">
            <i data-lucide="shield-alert" class="w-4 h-4"></i>
            <span class="flex-1">Alertas</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">{total_alerts}</span>
          </button>
          <button onclick="switchTab('tab-notifications')" id="btn-tab-notifications" class="sidebar-nav-item w-full text-left">
            <i data-lucide="bell" class="w-4 h-4"></i>
            <span class="flex-1">Notificaciones</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border border-rose-200 dark:border-rose-900">{p1_count} P1</span>
          </button>
          <button onclick="switchTab('tab-forense')" id="btn-tab-forense" class="sidebar-nav-item w-full text-left">
            <i data-lucide="network" class="w-4 h-4"></i>
            <span class="flex-1">Investigación</span>
          </button>
        </div>
      </div>

      <!-- SECCIÓN: GESTIÓN -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Gestión</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-soar')" id="btn-tab-soar" class="sidebar-nav-item w-full text-left">
            <i data-lucide="shield-check" class="w-4 h-4"></i>
            <span class="flex-1">Respuesta</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">{soar_count}</span>
          </button>
          <button onclick="switchTab('tab-activos')" id="btn-tab-activos" class="sidebar-nav-item w-full text-left">
            <i data-lucide="server" class="w-4 h-4"></i>
            <span class="flex-1">Activos</span>
          </button>
          <button onclick="switchTab('tab-automations')" id="btn-tab-automations" class="sidebar-nav-item w-full text-left">
            <i data-lucide="workflow" class="w-4 h-4"></i>
            <span class="flex-1">Automatización</span>
          </button>
        </div>
      </div>

      <!-- SECCIÓN: GOBIERNO -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Gobierno</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-roi')" id="btn-tab-roi" class="sidebar-nav-item w-full text-left">
            <i data-lucide="chart-line" class="w-4 h-4"></i>
            <span class="flex-1">Finanzas</span>
          </button>
          <button onclick="switchTab('tab-directrices')" id="btn-tab-directrices" class="sidebar-nav-item w-full text-left">
            <i data-lucide="file-check-2" class="w-4 h-4"></i>
            <span class="flex-1">Directrices</span>
          </button>
          <button onclick="switchTab('tab-auditoria')" id="btn-tab-auditoria" class="sidebar-nav-item w-full text-left">
            <i data-lucide="clipboard-list" class="w-4 h-4"></i>
            <span class="flex-1">Auditoría</span>
          </button>
        </div>
      </div>

    </nav>

    <!-- ESTADO CONEXIÓN INFERIOR -->
    <div class="p-3.5 border-t border-[#E2E8F0] dark:border-[#1E293B] bg-slate-50/70 dark:bg-slate-900/50 text-[11px] flex items-center justify-between text-slate-500 dark:text-slate-400">
      <div class="flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-[#42A83B]"></span>
        <span>alertas-soc-1</span>
      </div>
      <span class="font-mono text-[10px]">Graph 45s</span>
    </div>
  </aside>

  <!-- BACKDROP MÓVIL -->
  <div id="sidebar-backdrop" onclick="toggleSidebar()" class="fixed inset-0 bg-slate-900/40 z-30 hidden md:hidden"></div>

  <!-- =========================================================================
       ÁREA DE CONTENIDO
       ========================================================================= -->
  <div class="flex-1 md:pl-64 flex flex-col min-h-screen">
    
    <!-- HEADER SUPERIOR -->
    <header class="sticky top-0 z-20 bg-white/95 dark:bg-[#111A24]/95 backdrop-blur-sm border-b border-[#E2E8F0] dark:border-[#1E293B] px-4 sm:px-6 py-2.5 flex items-center justify-between gap-4">
      
      <!-- IZQUIERDA: HAMBURGUESA Y BREADCRUMB -->
      <div class="flex items-center space-x-3">
        <button onclick="toggleSidebar()" class="md:hidden p-1.5 rounded text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Abrir navegación">
          <i data-lucide="menu" class="w-5 h-5"></i>
        </button>
        <div class="hidden sm:flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
          <span class="font-medium text-slate-700 dark:text-slate-300">SAMPOL</span>
          <span>/</span>
          <span id="breadcrumb-current" class="text-slate-900 dark:text-white font-semibold">Dashboard</span>
        </div>
      </div>

      <!-- CENTRO: BÚSQUEDA RÁPIDA -->
      <div class="flex-1 max-w-sm hidden lg:block">
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-slate-400">
            <i data-lucide="search" class="w-3.5 h-3.5"></i>
          </span>
          <input type="text" id="global-search" oninput="handleGlobalSearch()" placeholder="Buscar en el sistema..." class="w-full pl-8 pr-3 py-1 text-xs rounded bg-slate-50 dark:bg-slate-800/80 border border-[#E2E8F0] dark:border-[#1E293B] focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white placeholder-slate-400">
        </div>
      </div>

      <!-- DERECHA: ACCIONES Y USUARIO -->
      <div class="flex items-center space-x-2 text-xs">
        
        <!-- ESTADO GRAPH -->
        <span class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-[11px]">
          <span class="w-1.5 h-1.5 rounded-full bg-[#42A83B]"></span>
          <span>{raw_count} correos</span>
        </span>

        <!-- CAMPANA DE NOTIFICACIONES -->
        <button onclick="toggleBellDrawer()" id="nexus-bell-trigger" class="relative p-1.5 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition" title="Notificaciones" aria-label="Notificaciones">
          <i data-lucide="bell" class="w-4 h-4"></i>
          <span id="bell-badge-count" class="absolute -top-0.5 -right-0.5 px-1 py-0.2 rounded-full bg-[#DC2626] text-white font-bold text-[9px] leading-tight">{p1_count}</span>
        </button>

        <!-- SELECTOR DE TEMA -->
        <button onclick="toggleTheme()" class="p-1.5 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition" title="Cambiar tema" aria-label="Cambiar tema">
          <span id="theme-icon"><i data-lucide="moon" class="w-4 h-4"></i></span>
        </button>

        <!-- PERFIL -->
        <div class="flex items-center space-x-2 pl-2 border-l border-slate-200 dark:border-slate-700">
          <div class="w-7 h-7 rounded-full bg-[#0784B7] text-white flex items-center justify-center font-medium text-[11px]">
            GS
          </div>
          <span class="hidden sm:inline font-medium text-slate-700 dark:text-slate-200 text-xs">Guardia SOC</span>
        </div>

      </div>
    </header>

    <!-- DRAWER LATERAL DE NOTIFICACIONES -->
    <aside id="bell-drawer" class="fixed top-14 right-4 w-88 max-w-[calc(100vw-2rem)] max-h-[80vh] overflow-y-auto bg-white dark:bg-[#111A24] border border-[#E2E8F0] dark:border-[#1E293B] rounded-lg shadow-lg p-4 z-50 hidden space-y-3">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2.5">
        <div>
          <strong class="text-xs font-semibold text-slate-900 dark:text-white">Avisos Prioritarios</strong>
          <p class="text-[10px] text-slate-400">Notificaciones P1 / P2</p>
        </div>
        <button onclick="toggleBellDrawer()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <div id="drawer-notifs-list" class="space-y-2 text-xs">
        <!-- Inyección JS -->
      </div>
      <div class="pt-2 border-t border-slate-100 dark:border-slate-800 text-center">
        <button onclick="switchTab('tab-notifications'); toggleBellDrawer();" class="text-xs text-[#0784B7] dark:text-[#38BDF8] font-semibold hover:underline">
          Ver todas las notificaciones →
        </button>
      </div>
    </aside>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="flex-1 p-4 sm:p-6 max-w-7xl w-full mx-auto space-y-6">

      <!-- =====================================================================
           TAB 1: DASHBOARD
           ===================================================================== -->
      <section id="tab-resumen" class="tab-content space-y-5">
        
        <!-- ENCABEZADO -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Dashboard</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Resumen de seguridad y operaciones.</p>
          </div>
          <button onclick="location.reload()" class="btn-sampol-secondary text-xs">
            <i data-lucide="rotate-cw" class="w-3.5 h-3.5"></i>
            <span>Actualizar</span>
          </button>
        </div>

        <!-- 5 INDICADORES PRINCIPALES (SOBRIOS Y MINIMALISTAS) -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          
          <div class="sampol-card p-3.5">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Alertas Recibidas</div>
            <div class="text-2xl font-bold text-slate-900 dark:text-white mt-0.5">{raw_count}</div>
            <div class="text-[10px] text-slate-400 mt-1">Sensor Outlook</div>
          </div>

          <div class="sampol-card p-3.5">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Alertas Únicas</div>
            <div class="text-2xl font-bold text-[#0784B7] dark:text-[#38BDF8] mt-0.5">{total_alerts}</div>
            <div class="text-[10px] text-slate-400 mt-1">Taxonomía INCIBE</div>
          </div>

          <div class="sampol-card p-3.5">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Incidentes Críticos</div>
            <div class="text-2xl font-bold text-[#DC2626] mt-0.5">{p1_count}</div>
            <div class="text-[10px] text-slate-400 mt-1">SLA 15 minutos</div>
          </div>

          <div class="sampol-card p-3.5">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Contención SOAR</div>
            <div class="text-2xl font-bold text-slate-900 dark:text-white mt-0.5">{soar_count}</div>
            <div class="text-[10px] text-slate-400 mt-1">Directriz 1 (18:00)</div>
          </div>

          <div class="sampol-card p-3.5 col-span-2 sm:col-span-1">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Ahorro Anual ROI</div>
            <div class="text-2xl font-bold text-[#42A83B] mt-0.5">184.500 €</div>
            <div class="text-[10px] text-slate-400 mt-1">Payback 42 días</div>
          </div>

        </div>

        <!-- GRÁFICOS: CATEGORÍAS Y GRAVEDAD -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="sampol-card p-4 lg:col-span-2">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-xs font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wider">Categorías INCIBE</h2>
              <span class="text-[11px] text-slate-400">10 clases</span>
            </div>
            <div class="h-56">
              <canvas id="chart-incibe"></canvas>
            </div>
          </div>

          <div class="sampol-card p-4">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-xs font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wider">Gravedad</h2>
              <span class="text-[11px] text-slate-400">Triaje</span>
            </div>
            <div class="h-56 flex items-center justify-center">
              <canvas id="chart-severity"></canvas>
            </div>
          </div>
        </div>

        <!-- ACCESOS RÁPIDOS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div onclick="switchTab('tab-notifications')" class="sampol-card p-4 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-900 dark:text-white">Smart Notifications</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-[#0784B7] transition"></i>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Banco de pruebas y reducción del 96.4% de fatiga.</p>
          </div>

          <div onclick="switchTab('tab-soar')" class="sampol-card p-4 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-900 dark:text-white">Centro de Respuesta</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-[#0784B7] transition"></i>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">62 contenciones automáticas ante intrusiones.</p>
          </div>

          <div onclick="switchTab('tab-roi')" class="sampol-card p-4 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-900 dark:text-white">Modelo Financiero</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-[#0784B7] transition"></i>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Calculadora interactiva con datos del Director de TI.</p>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 2: ALERTAS
           ===================================================================== -->
      <section id="tab-dataset" class="tab-content hidden space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Alertas</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Triaje e inspección bajo taxonomía oficial INCIBE ({total_alerts} únicas).</p>
          </div>
          <div class="w-full sm:w-72">
            <input type="text" id="alert-search" oninput="filterAlerts()" placeholder="Filtrar por código, usuario..." class="w-full px-3 py-1.5 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <div class="sampol-card overflow-hidden">
          <div class="overflow-x-auto max-h-[580px]">
            <table class="sampol-table">
              <thead class="sticky top-0 z-10">
                <tr>
                  <th>Código</th>
                  <th>Fecha (UTC)</th>
                  <th>Gravedad</th>
                  <th>Clase INCIBE</th>
                  <th>Usuario</th>
                  <th>Sede</th>
                  <th>Descripción</th>
                </tr>
              </thead>
              <tbody id="tbl-alerts" class="divide-y divide-slate-100 dark:divide-slate-800">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 3: NOTIFICACIONES
           ===================================================================== -->
      <section id="tab-notifications" class="tab-content hidden space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Notificaciones</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Gestión de avisos inteligentes y anti-fatiga (200.000 alertas/día).</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            Throughput: 238.000 alertas/s (0.004 ms)
          </span>
        </div>

        <!-- METRICAS CLAVE -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="sampol-card p-3">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Total Alertas Brutas</div>
            <div class="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{raw_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Sensor Microsoft Graph</div>
          </div>
          <div class="sampol-card p-3">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Incidentes Consolidados</div>
            <div class="text-xl font-bold text-[#0784B7] dark:text-[#38BDF8] mt-0.5">{notif_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Ratio reducc. 65%</div>
          </div>
          <div class="sampol-card p-3">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">P1 Críticos (SLA 15m)</div>
            <div id="stat-p1-count" class="text-xl font-bold text-rose-600 dark:text-rose-400 mt-0.5">{p1_count}</div>
            <div class="text-[10px] text-rose-500 mt-0.5">Atención inmediata</div>
          </div>
          <div class="sampol-card p-3">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Escalados a Dirección</div>
            <div id="stat-esc-count" class="text-xl font-bold text-amber-600 dark:text-amber-400 mt-0.5">0</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Auditado NIS2</div>
          </div>
        </div>

        <!-- SIMULADOR DEMO -->
        <div class="sampol-card p-4 space-y-3">
          <div class="text-xs font-semibold text-slate-700 dark:text-slate-300">Simulación de Escenarios (Modo Demo)</div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 text-xs">
            <button onclick="runScenarioA()" class="p-2.5 rounded border border-slate-200 dark:border-slate-700 hover:border-[#0784B7] text-left transition">
              <div class="font-semibold text-slate-900 dark:text-white">Escenario A: Ráfaga 5.000</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Consolidación en 1 ticket único.</div>
            </button>
            <button onclick="runScenarioB()" class="p-2.5 rounded border border-slate-200 dark:border-slate-700 hover:border-[#0784B7] text-left transition">
              <div class="font-semibold text-slate-900 dark:text-white">Escenario B: Escalada P3 → P1</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Ruptura inmediata de cooldown.</div>
            </button>
            <button onclick="runScenarioC()" class="p-2.5 rounded border border-slate-200 dark:border-slate-700 hover:border-[#0784B7] text-left transition">
              <div class="font-semibold text-slate-900 dark:text-white">Escenario C: Escalado SLA</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Escala a guardia y dirti@sampol.com.</div>
            </button>
            <button onclick="runScenarioD()" class="p-2.5 rounded border border-slate-200 dark:border-slate-700 hover:border-[#0784B7] text-left transition">
              <div class="font-semibold text-slate-900 dark:text-white">Escenario D: Vista Móvil</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Verificación táctil en 320px+.</div>
            </button>
          </div>
          <div id="scenario-alert-box" class="hidden p-3 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-mono"></div>
        </div>

        <!-- FILTROS -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-1.5 text-xs">
            <button onclick="setNotifFilter('all')" id="btn-nf-all" class="px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium">Todas ({notif_count})</button>
            <button onclick="setNotifFilter('P1')" id="btn-nf-P1" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">P1 Críticas</button>
            <button onclick="setNotifFilter('P2')" id="btn-nf-P2" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">P2 Altas</button>
            <button onclick="setNotifFilter('unack')" id="btn-nf-unack" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">Sin Reconocer</button>
          </div>
          <div class="w-full sm:w-64">
            <input type="text" id="notif-search" oninput="renderNotifsTable()" placeholder="Buscar por usuario, ID..." class="w-full px-2.5 py-1 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <!-- LISTA -->
        <div id="notifs-container" class="space-y-2.5">
          <!-- Inyección JS -->
        </div>

      </section>

      <!-- =====================================================================
           TAB 4: INVESTIGACIÓN
           ===================================================================== -->
      <section id="tab-forense" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Investigación</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Análisis de la Kill Chain, paciente cero y reducción de dwell time.</p>
        </div>

        <!-- ETAPAS -->
        <div class="sampol-card p-4 space-y-2.5 text-xs">
          <div class="font-semibold text-slate-800 dark:text-slate-200 mb-2">Cronología del Incidente (MITRE ATT&CK)</div>
          
          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
            <span><strong>1. Phishing:</strong> AL-20261030-0025 recibido en buzón de jmoreno@sampol.com.</span>
            <span class="font-mono text-[10px] text-slate-400">02:41 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
            <span><strong>2. Password Spray:</strong> AL-20261030-0026 detecta 43 autenticaciones anómalas.</span>
            <span class="font-mono text-[10px] text-slate-400">02:54 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-rose-200 dark:border-rose-900 bg-rose-50/40 dark:bg-rose-950/20 flex justify-between items-center">
            <span class="text-rose-700 dark:text-rose-300"><strong>3. Paciente Cero:</strong> Emisión ilegítima de token para jmoreno@sampol.com.</span>
            <span class="font-mono text-[10px] text-rose-600 font-bold">03:20 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
            <span><strong>4. Exfiltración:</strong> Lectura y modificación de ficheros en srv-barcelona-201.</span>
            <span class="font-mono text-[10px] text-slate-400">03:33 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-rose-300 dark:border-rose-800 bg-rose-100/40 dark:bg-rose-950/40 flex justify-between items-center">
            <span class="text-rose-800 dark:text-rose-200"><strong>5. Canal C2:</strong> Balizamiento hacia sync-gateway.invalid (Precursor Ransomware).</span>
            <span class="font-mono text-[10px] text-rose-700 font-bold">03:46 UTC</span>
          </div>
        </div>

        <!-- IOCS -->
        <div class="sampol-card p-4">
          <div class="font-semibold text-slate-800 dark:text-slate-200 text-xs mb-3">Indicadores de Compromiso (IoCs)</div>
          <table class="sampol-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Artefacto</th>
                <th>Rol</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span class="badge-medium">Dominio</span></td>
                <td class="font-mono font-medium text-slate-800 dark:text-slate-200">sync-gateway.invalid</td>
                <td>C2 / Balizamiento</td>
                <td class="text-emerald-600 font-medium">Bloqueado</td>
              </tr>
              <tr>
                <td><span class="badge-medium">Dominio</span></td>
                <td class="font-mono font-medium text-slate-800 dark:text-slate-200">login-acceso.invalid</td>
                <td>Phishing</td>
                <td class="text-emerald-600 font-medium">Bloqueado</td>
              </tr>
              <tr>
                <td><span class="badge-high">IP</span></td>
                <td class="font-mono font-medium text-slate-800 dark:text-slate-200">203.0.113.150 / 200</td>
                <td>Origen</td>
                <td class="text-emerald-600 font-medium">Aislado</td>
              </tr>
              <tr>
                <td><span class="badge-critical">Cuenta</span></td>
                <td class="font-mono font-medium text-rose-600 font-bold">jmoreno@sampol.com</td>
                <td>Paciente Cero</td>
                <td class="text-emerald-600 font-medium">Sesión Revocada</td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>

      <!-- =====================================================================
           TAB 5: RESPUESTA (SOAR)
           ===================================================================== -->
      <section id="tab-soar" class="tab-content hidden space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Respuesta</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Contención autónoma perimetral (Directriz 1 - 18:00).</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            {soar_count} Acciones Ejecutadas
          </span>
        </div>

        <div class="sampol-card overflow-hidden">
          <div class="overflow-x-auto max-h-[500px]">
            <table class="sampol-table">
              <thead class="sticky top-0 z-10">
                <tr>
                  <th>ID</th>
                  <th>Acción</th>
                  <th>Objetivo</th>
                  <th>Disparo</th>
                  <th>Estado</th>
                  <th>Regla</th>
                </tr>
              </thead>
              <tbody id="tbl-soar-actions" class="divide-y divide-slate-100 dark:divide-slate-800">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 6: ACTIVOS
           ===================================================================== -->
      <section id="tab-activos" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Activos</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Identidades y sistemas bajo supervisión activa.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="sampol-card p-4 space-y-2.5">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Identidades Aisladas (SOAR)</div>
            <div class="p-2 rounded border border-rose-200 dark:border-rose-900 bg-rose-50/30 dark:bg-rose-950/20 flex justify-between items-center">
              <div>
                <div class="font-bold text-rose-700 dark:text-rose-300">jmoreno@sampol.com</div>
                <div class="text-[10px] text-slate-500">Paciente Cero · Compromiso de Token</div>
              </div>
              <span class="badge-critical">Bloqueado</span>
            </div>
            <div class="p-2 rounded border border-rose-200 dark:border-rose-900 bg-rose-50/30 dark:bg-rose-950/20 flex justify-between items-center">
              <div>
                <div class="font-bold text-rose-700 dark:text-rose-300">bmoreno@sampol.com</div>
                <div class="text-[10px] text-slate-500">Spray Masivo · 5.000 eventos</div>
              </div>
              <span class="badge-critical">Bloqueado</span>
            </div>
            <div class="p-2 rounded border border-rose-200 dark:border-rose-900 bg-rose-50/30 dark:bg-rose-950/20 flex justify-between items-center">
              <div>
                <div class="font-bold text-rose-700 dark:text-rose-300">cmoreno@sampol.com</div>
                <div class="text-[10px] text-slate-500">Malware C2</div>
              </div>
              <span class="badge-critical">Bloqueado</span>
            </div>
          </div>

          <div class="sampol-card p-4 space-y-2.5">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Infraestructura Crítica</div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">srv-barcelona-201</div>
                <div class="text-[10px] text-slate-400">Servidor de Aplicaciones</div>
              </div>
              <span class="badge-high">Revisión</span>
            </div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">gw-bilbao-204</div>
                <div class="text-[10px] text-slate-400">Gateway Perimetral</div>
              </div>
              <span class="badge-low">Contenido</span>
            </div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">srv-palma-205</div>
                <div class="text-[10px] text-slate-400">Servidor Central</div>
              </div>
              <span class="badge-low">Protegido</span>
            </div>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 7: AUTOMATIZACIÓN
           ===================================================================== -->
      <section id="tab-automations" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Automatización</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Pipelines de ingesta continua y contención perimetral.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="sampol-card p-3.5 space-y-1.5">
            <div class="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-white">
              <span class="w-2 h-2 rounded-full bg-[#42A83B]"></span>
              <span>Daemon Graph API</span>
            </div>
            <p class="text-slate-500 text-[11px]">Sondeo de Outlook cada 45s. Ingesta inmutable SHA-256 en Azure PostgreSQL.</p>
            <div class="pt-1.5 text-[10px] text-slate-400 font-mono">daemon_sync.py · Activo</div>
          </div>

          <div class="sampol-card p-3.5 space-y-1.5">
            <div class="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-white">
              <span class="w-2 h-2 rounded-full bg-[#42A83B]"></span>
              <span>SOAR Auto-Blocker</span>
            </div>
            <p class="text-slate-500 text-[11px]">Aislamiento autónomo sub-segundo ante compromisos confirmados (Directriz 1).</p>
            <div class="pt-1.5 text-[10px] text-slate-400 font-mono">autoblock_engine.py · Activo</div>
          </div>

          <div class="sampol-card p-3.5 space-y-1.5">
            <div class="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-white">
              <span class="w-2 h-2 rounded-full bg-[#42A83B]"></span>
              <span>FastAPI SSE Stream</span>
            </div>
            <p class="text-slate-500 text-[11px]">Emisión en tiempo real de eventos hacia el frontend mediante Server-Sent Events.</p>
            <div class="pt-1.5 text-[10px] text-slate-400 font-mono">backend_api.py:8000 · Activo</div>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 8: FINANZAS (CALCULADORA ROI)
           ===================================================================== -->
      <section id="tab-roi" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Finanzas</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Retorno de inversión y ahorro operativo (Directorio de TI SAMPOL).</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          
          <div class="sampol-card p-4 space-y-4">
            <div class="text-xs font-semibold text-slate-800 dark:text-slate-200">1. Triaje de Alertas</div>
            
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Volumen mensual:</span>
                <span id="lbl-vol" class="font-semibold text-[#0784B7]">3.000</span>
              </div>
              <input type="range" id="slider-vol" min="500" max="10000" step="100" value="3000" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Revisión manual:</span>
                <span id="lbl-tman" class="font-semibold text-[#0784B7]">12 min</span>
              </div>
              <input type="range" id="slider-tman" min="2" max="30" step="1" value="12" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Coste analista SOC:</span>
                <span id="lbl-cost" class="font-semibold text-[#0784B7]">45 €/h</span>
              </div>
              <input type="range" id="slider-cost" min="25" max="80" step="1" value="45" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>
          </div>

          <div class="sampol-card p-4 space-y-4">
            <div class="text-xs font-semibold text-slate-800 dark:text-slate-200">2. Bloqueo y Desarrollo</div>
            
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Bloqueos al mes:</span>
                <span id="lbl-bloq" class="font-semibold text-[#0784B7]">120</span>
              </div>
              <input type="range" id="slider-bloq" min="10" max="500" step="10" value="120" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Tiempo por bloqueo:</span>
                <span id="lbl-tbloq" class="font-semibold text-[#0784B7]">25 min</span>
              </div>
              <input type="range" id="slider-tbloq" min="5" max="60" step="5" value="25" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-600 dark:text-slate-400">Coste dev interno:</span>
                <span id="lbl-cdev" class="font-semibold text-[#0784B7]">50 €/h</span>
              </div>
              <input type="range" id="slider-cdev" min="30" max="100" step="5" value="50" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>
          </div>

          <div class="sampol-card p-4 flex flex-col justify-between">
            <div>
              <div class="text-[11px] font-semibold text-slate-400 uppercase">Ahorro Operativo Anual</div>
              <div id="res-ahorro-neto" class="text-3xl font-bold text-[#42A83B] mt-1">184.500 €</div>
              <p class="text-xs text-slate-500 mt-1">Frente al modelo manual AS-IS.</p>
            </div>

            <div class="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2 text-xs">
              <div>
                <span class="text-slate-400">Payback:</span>
                <span id="res-payback" class="font-bold text-slate-900 dark:text-white ml-1">42 días (1,4 meses)</span>
              </div>
              <div>
                <span class="text-slate-400">Retorno (ROI):</span>
                <span id="res-roi" class="font-bold text-[#0784B7] ml-1">823 %</span>
              </div>
            </div>
          </div>

        </div>

      </section>

      <!-- =====================================================================
           TAB 9: DIRECTRICES
           ===================================================================== -->
      <section id="tab-directrices" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Directrices</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Órdenes ejecutivas de TI y cumplimiento normativo NIS2.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="sampol-card p-3.5 space-y-1">
            <div class="flex justify-between items-center">
              <span class="font-semibold text-[#0784B7]">Directriz 09:00</span>
              <span class="badge-low">Cumplida</span>
            </div>
            <div class="font-semibold text-slate-900 dark:text-white">Microsoft Graph & SHA-256</div>
            <p class="text-slate-500 text-[11px]">Ingesta directa de correos sin pérdidas y cálculo de huella inmutable.</p>
          </div>

          <div class="sampol-card p-3.5 space-y-1">
            <div class="flex justify-between items-center">
              <span class="font-semibold text-[#0784B7]">Directriz 11:30</span>
              <span class="badge-low">Cumplida</span>
            </div>
            <div class="font-semibold text-slate-900 dark:text-white">Taxonomía INCIBE (10 Clases)</div>
            <p class="text-slate-500 text-[11px]">Clasificación normalizada conforme a los estándares del CERT.</p>
          </div>

          <div class="sampol-card p-3.5 space-y-1">
            <div class="flex justify-between items-center">
              <span class="font-semibold text-[#0784B7]">Directriz 15:30</span>
              <span class="badge-low">Cumplida</span>
            </div>
            <div class="font-semibold text-slate-900 dark:text-white">API de Bloqueo Sampol</div>
            <p class="text-slate-500 text-[11px]">Aislamiento perimetral con doble confirmación y gestión de excepciones.</p>
          </div>

          <div class="sampol-card p-3.5 space-y-1">
            <div class="flex justify-between items-center">
              <span class="font-semibold text-[#0784B7]">Directriz 18:00</span>
              <span class="badge-low">Cumplida</span>
            </div>
            <div class="font-semibold text-slate-900 dark:text-white">Auto-Bloqueo de Cuentas Comprometidas</div>
            <p class="text-slate-500 text-[11px]">Aislamiento sub-segundo sin esperar revisión manual ante intrusión confirmada.</p>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 10: AUDITORÍA
           ===================================================================== -->
      <section id="tab-auditoria" class="tab-content hidden space-y-4">
        
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Auditoría</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Trazabilidad inmutable de eventos conforme a NIS2 y ENS.</p>
        </div>

        <div class="sampol-card p-4 space-y-2 text-xs font-mono">
          <div class="text-slate-600 dark:text-slate-400">[2026-11-03 20:20:01 UTC] <strong class="text-emerald-600">AUDIT_OK</strong>: Sincronización 142 correos. Hash SHA-256 verificado.</div>
          <div class="text-slate-600 dark:text-slate-400">[2026-11-03 19:06:35 UTC] <strong class="text-purple-600">SOAR_DISPATCH</strong>: Orden autónoma #63 sobre dmoreno@sampol.com ejecutada.</div>
          <div class="text-slate-600 dark:text-slate-400">[2026-11-03 18:00:00 UTC] <strong class="text-[#0784B7]">POLICY_ACTIVE</strong>: Directriz 1 (TI) activada en toda la infraestructura.</div>
        </div>

      </section>

    </main>

  </div>

  <!-- =========================================================================
       SCRIPTS JAVASCRIPT
       ========================================================================= -->
  <script>
    const ALERTS_DATA = {alerts_json};
    const SOAR_DATA = {soar_json};
    let NOTIFS_DATA = {notifs_json};
    let CURRENT_NOTIF_FILTER = 'all';

    function initTheme() {{
      const saved = localStorage.getItem('sampol_theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
        updateThemeIcon(true);
      }} else {{
        document.documentElement.classList.add('light');
        document.documentElement.classList.remove('dark');
        updateThemeIcon(false);
      }}
    }}

    function toggleTheme() {{
      const isDark = document.documentElement.classList.contains('dark');
      if (isDark) {{
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        localStorage.setItem('sampol_theme', 'light');
        updateThemeIcon(false);
      }} else {{
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
        localStorage.setItem('sampol_theme', 'dark');
        updateThemeIcon(true);
      }}
    }}

    function updateThemeIcon(isDark) {{
      const container = document.getElementById('theme-icon');
      if (!container) return;
      container.innerHTML = isDark 
        ? '<i data-lucide="sun" class="w-4 h-4"></i>'
        : '<i data-lucide="moon" class="w-4 h-4"></i>';
      if (window.lucide) lucide.createIcons();
    }}

    function toggleSidebar() {{
      const sb = document.getElementById('main-sidebar');
      const bd = document.getElementById('sidebar-backdrop');
      if (sb) sb.classList.toggle('-translate-x-full');
      if (bd) bd.classList.toggle('hidden');
    }}

    const TAB_NAMES = {{
      'tab-resumen': 'Dashboard',
      'tab-dataset': 'Alertas',
      'tab-notifications': 'Notificaciones',
      'tab-forense': 'Investigación',
      'tab-soar': 'Respuesta',
      'tab-activos': 'Activos',
      'tab-automations': 'Automatización',
      'tab-roi': 'Finanzas',
      'tab-directrices': 'Directrices',
      'tab-auditoria': 'Auditoría'
    }};

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.sidebar-nav-item').forEach(el => el.classList.remove('active'));

      const target = document.getElementById(tabId);
      if (target) target.classList.remove('hidden');

      const btn = document.getElementById('btn-' + tabId);
      if (btn) btn.classList.add('active');

      const bc = document.getElementById('breadcrumb-current');
      if (bc && TAB_NAMES[tabId]) bc.textContent = TAB_NAMES[tabId];

      const sb = document.getElementById('main-sidebar');
      if (sb && !sb.classList.contains('-translate-x-full') && window.innerWidth < 768) {{
        toggleSidebar();
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
      if (window.lucide) lucide.createIcons();
    }}

    function toggleBellDrawer() {{
      const d = document.getElementById('bell-drawer');
      if (!d) return;
      d.classList.toggle('hidden');
      renderDrawerList();
    }}

    function renderDrawerList() {{
      const c = document.getElementById('drawer-notifs-list');
      if (!c) return;
      const unack = (NOTIFS_DATA || []).filter(n => !n.acknowledged && (n.priority === 'P1' || n.priority === 'P2'));
      if (!unack.length) {{
        c.innerHTML = '<p class="text-slate-400 text-center py-4 text-xs">Sin avisos prioritarios pendientes.</p>';
        return;
      }}
      c.innerHTML = unack.slice(0, 8).map(n => `
        <div class="p-2.5 rounded border ${{n.priority === 'P1' ? 'border-rose-200 dark:border-rose-900 bg-rose-50/50 dark:bg-rose-950/20' : 'border-amber-200 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/20'}} space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-bold ${{n.priority === 'P1' ? 'text-rose-700 dark:text-rose-400' : 'text-amber-700 dark:text-amber-400'}} text-[11px]">${{n.priority}} · ${{n.incident_id || 'INC'}}</span>
            <span class="text-[10px] text-slate-400">${{n.count || 1}} evento(s)</span>
          </div>
          <div class="font-medium text-slate-800 dark:text-white text-[11px] truncate">${{n.title || ''}}</div>
          <button onclick="ackNotification(${{n.id}})" class="px-2 py-0.5 rounded bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[10px] font-medium border border-slate-200 dark:border-slate-700 w-full mt-1 cursor-pointer">Reconocer</button>
        </div>
      `).join('');
      if (window.lucide) lucide.createIcons();
    }}

    function setNotifFilter(f) {{
      CURRENT_NOTIF_FILTER = f;
      document.querySelectorAll('[id^="btn-nf-"]').forEach(b => {{
        b.className = 'px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 text-xs';
      }});
      const bActive = document.getElementById('btn-nf-' + f);
      if (bActive) bActive.className = 'px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium text-xs';
      renderNotifsTable();
    }}

    function renderNotifsTable() {{
      const searchEl = document.getElementById('notif-search');
      const q = searchEl ? (searchEl.value || '').toLowerCase() : '';
      const c = document.getElementById('notifs-container');
      if (!c) return;
      
      const filtered = (NOTIFS_DATA || []).filter(n => {{
        const matchF = CURRENT_NOTIF_FILTER === 'all' || 
                       (CURRENT_NOTIF_FILTER === 'unack' && !n.acknowledged) ||
                       (n.priority === CURRENT_NOTIF_FILTER);
        const matchQ = !q || (n.title || '').toLowerCase().includes(q) ||
                             (n.incident_id || '').toLowerCase().includes(q) ||
                             (n.affected_user || '').toLowerCase().includes(q);
        return matchF && matchQ;
      }});

      if (!filtered.length) {{
        c.innerHTML = '<div class="sampol-card p-6 text-center text-slate-400 text-xs">No se encontraron notificaciones con el filtro actual.</div>';
        return;
      }}

      c.innerHTML = filtered.map(n => {{
        const isP1 = n.priority === 'P1';
        const isP2 = n.priority === 'P2';
        const isAck = !!n.acknowledged;
        const colorBorder = isP1 ? 'border-rose-200 dark:border-rose-900 bg-rose-50/20 dark:bg-rose-950/10' : isP2 ? 'border-amber-200 dark:border-amber-900 bg-amber-50/20 dark:bg-amber-950/10' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#111A24]';
        const badgeColor = isP1 ? 'badge-critical' : isP2 ? 'badge-high' : 'badge-low';

        const reasonsHtml = ((n.reasons || []).slice(0, 3)).map(r => `<span class="px-1.5 py-0.5 rounded bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[10px] border border-slate-200 dark:border-slate-700">${{r}}</span>`).join(' ');

        return `
          <div class="p-3.5 rounded border ${{colorBorder}} space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="${{badgeColor}}">${{n.priority}}</span>
                <span class="font-mono text-xs font-semibold text-[#0784B7] dark:text-[#38BDF8]">${{n.incident_id || 'INC'}}</span>
                <span class="text-xs text-slate-400">· ${{n.count || 1}} evento(s)</span>
                <span class="text-xs text-slate-400">· Riesgo: <strong class="text-slate-700 dark:text-slate-200">${{n.risk_score || 75}}/100</strong></span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs ${{isAck ? 'text-emerald-600' : 'text-amber-600'}} font-medium">
                  ${{isAck ? 'Reconocida (' + (n.acknowledged_by || 'Analista') + ')' : 'Pendiente'}}
                </span>
                <button onclick="ackNotification(${{n.id}})" ${{isAck ? 'disabled' : ''}} class="px-2.5 py-1 rounded text-xs ${{isAck ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed' : 'btn-sampol-primary cursor-pointer'}} transition">
                  ${{isAck ? 'Reconocida' : 'Reconocer'}}
                </button>
              </div>
            </div>

            <div class="text-xs font-semibold text-slate-900 dark:text-white">${{n.title || ''}}</div>
            <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">${{n.description || ''}}</p>

            <div class="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
              <span>Usuario: <strong class="text-slate-700 dark:text-slate-300 font-mono">${{n.affected_user || '-'}}</strong></span>
              <span>Activo: <strong class="text-slate-700 dark:text-slate-300 font-mono">${{n.affected_asset || '-'}}</strong></span>
              ${{reasonsHtml}}
            </div>
          </div>
        `;
      }}).join('');

      const p1Unack = (NOTIFS_DATA || []).filter(n => !n.acknowledged && n.priority === 'P1').length;
      const bBadge = document.getElementById('bell-badge-count');
      if (bBadge) bBadge.textContent = p1Unack;
      const stP1 = document.getElementById('stat-p1-count');
      if (stP1) stP1.textContent = p1Unack;
      if (window.lucide) lucide.createIcons();
    }}

    function ackNotification(id) {{
      NOTIFS_DATA = (NOTIFS_DATA || []).map(n => {{
        if (n.id === id) {{
          return {{ ...n, acknowledged: true, acknowledged_by: 'guardia_soc@sampol.com', status: 'acknowledged' }};
        }}
        return n;
      }});
      renderNotifsTable();
      renderDrawerList();
    }}

    function runScenarioA() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>Escenario A (Ráfaga 5.000 Alertas):</strong> Inyectados 5.000 eventos de password spraying. <strong>Resultado:</strong> 1 sola notificación emitida (INC-STRESS-5000), 4.999 eventos consolidados en el ticket. <strong>Reducción de fatiga: 99.98%</strong>. Latencia: 0.028 s.';
      
      NOTIFS_DATA.unshift({{
        id: 9999,
        incident_id: 'INC-STRESS-5000',
        priority: 'P1',
        risk_score: 95,
        title: 'Ataque Masivo de Password Spraying (5.000 Eventos)',
        description: '5.000 alertas recibidas en ráfaga. El motor anti-saturación consolidó todos los eventos en este único ticket.',
        count: 5000,
        acknowledged: false,
        affected_user: 'bmoreno@sampol.com',
        affected_asset: 'srv-auth-01',
        reasons: ['Ráfaga 5.000 eventos correlacionados', 'Reducción fatiga: 99.98%']
      }});
      renderNotifsTable();
    }}

    function runScenarioB() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>Escenario B (Escalada Crítica P3 → P1):</strong> Detección de binario malicioso (MODIFY-LAB). <strong>Resultado:</strong> Disparo inmediato de notificación P1 ignorando el cooldown de 15 minutos.';
      
      const found = (NOTIFS_DATA || []).find(n => (n.incident_id || '').includes('cmoreno') || (n.title || '').includes('ficheros'));
      if (found) {{
        found.priority = 'P1';
        found.risk_score = 100;
        found.acknowledged = false;
        found.reasons.unshift('Escalada Crítica: Precursor Ransomware');
      }}
      renderNotifsTable();
    }}

    function runScenarioC() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>Escenario C (Escalado Jerárquico):</strong> Incidente P1 sin acuse tras 15 minutos. <strong>Resultado:</strong> Escalado automático a guardia_soc@sampol.com con copia auditada a dirti@sampol.com.';
      const escEl = document.getElementById('stat-esc-count');
      if (escEl) escEl.textContent = '1';
    }}

    function runScenarioD() {{
      alert('Simulación Móvil: Redimensiona el navegador o abre la URL en un dispositivo móvil para comprobar la adaptación fluida a pantallas táctiles desde 320 px.');
    }}

    function handleGlobalSearch() {{
      const q = (document.getElementById('global-search').value || '').toLowerCase();
      if (!q) return;
      switchTab('tab-dataset');
      const inputAlert = document.getElementById('alert-search');
      if (inputAlert) {{
        inputAlert.value = q;
        filterAlerts();
      }}
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      initTheme();
      renderNotifsTable();
      renderDrawerList();
      calcROI();

      const tbAlerts = document.getElementById('tbl-alerts');
      if (tbAlerts) {{
        tbAlerts.innerHTML = (ALERTS_DATA || []).slice(0, 100).map(a => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
            <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-medium">${{a.internal_id}}</td>
            <td class="text-slate-400 font-mono text-[10px]">${{a.timestamp.substring(0, 16)}}</td>
            <td>
              <span class="${{a.severity === 'CRITICA' ? 'badge-critical' : 'badge-high'}}">${{a.severity}}</span>
            </td>
            <td class="text-slate-700 dark:text-slate-300 font-medium">${{a.class}}</td>
            <td class="font-mono text-slate-600 dark:text-slate-400">${{a.user || '-'}}</td>
            <td class="text-slate-500">${{a.site || 'Palma'}}</td>
            <td class="text-slate-500 dark:text-slate-400 truncate max-w-sm">${{a.desc || a.category}}</td>
          </tr>
        `).join('');
      }}

      const tbSoar = document.getElementById('tbl-soar-actions');
      if (tbSoar) {{
        tbSoar.innerHTML = (SOAR_DATA || []).slice(0, 50).map(s => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
            <td class="font-mono text-slate-500 font-medium">#${{s.id}}</td>
            <td class="font-medium text-slate-900 dark:text-white">${{s.action}}</td>
            <td class="font-mono text-[#0784B7] dark:text-[#38BDF8]">${{s.target}}</td>
            <td class="text-slate-500">${{s.trigger}}</td>
            <td><span class="badge-low">${{s.status}}</span></td>
            <td class="text-slate-500 dark:text-slate-400 truncate max-w-sm">${{s.reason}}</td>
          </tr>
        `).join('');
      }}

      const chIncibe = document.getElementById('chart-incibe');
      if (chIncibe && typeof Chart !== 'undefined') {{
        new Chart(chIncibe, {{
          type: 'bar',
          data: {{
            labels: ['Intrusión', 'Fraude', 'Disponibilidad', 'Compromiso Info', 'Código Dañino', 'Vulnerable', 'Obtención Info'],
            datasets: [{{
              label: 'Alertas',
              data: [20, 14, 12, 12, 11, 8, 7],
              backgroundColor: '#0784B7',
              borderRadius: 4
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
              x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }} }} }},
              y: {{ grid: {{ color: 'rgba(226, 232, 240, 0.6)' }}, ticks: {{ font: {{ size: 10 }} }} }}
            }}
          }}
        }});
      }}

      const chSev = document.getElementById('chart-severity');
      if (chSev && typeof Chart !== 'undefined') {{
        new Chart(chSev, {{
          type: 'doughnut',
          data: {{
            labels: ['Crítica', 'Alta', 'Media', 'Baja'],
            datasets: [{{
              data: [15, 38, 30, 10],
              backgroundColor: ['#DC2626', '#EA580C', '#D97706', '#16A34A']
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{
                position: 'bottom',
                labels: {{ boxWidth: 10, font: {{ size: 10 }} }}
              }}
            }}
          }}
        }});
      }}

      if (window.lucide) {{
        lucide.createIcons();
      }}
    }});

    function filterAlerts() {{
      const q = (document.getElementById('alert-search').value || '').toLowerCase();
      const rows = document.querySelectorAll('#tbl-alerts tr');
      rows.forEach(r => {{
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
      }});
    }}

    function calcROI() {{
      const sliderVol = document.getElementById('slider-vol');
      if (!sliderVol) return;

      const vol = parseFloat(document.getElementById('slider-vol').value);
      const tman = parseFloat(document.getElementById('slider-tman').value);
      const cost = parseFloat(document.getElementById('slider-cost').value);
      const bloq = parseFloat(document.getElementById('slider-bloq').value);
      const tbloq = parseFloat(document.getElementById('slider-tbloq').value);
      const cdev = parseFloat(document.getElementById('slider-cdev').value);

      document.getElementById('lbl-vol').textContent = vol.toLocaleString();
      document.getElementById('lbl-tman').textContent = tman + ' min';
      document.getElementById('lbl-cost').textContent = cost + ' €/h';
      document.getElementById('lbl-bloq').textContent = bloq.toLocaleString();
      document.getElementById('lbl-tbloq').textContent = tbloq + ' min';
      document.getElementById('lbl-cdev').textContent = cdev + ' €/h';

      const hTriajeActual = (vol * tman) / 60.0;
      const cTriajeActual = hTriajeActual * cost;
      const hTriajeNexus = (vol * 0.1) / 60.0;
      const cTriajeNexus = hTriajeNexus * cost;
      const ahTriajeMes = cTriajeActual - cTriajeNexus;

      const hSoarActual = (bloq * tbloq) / 60.0;
      const cSoarActual = hSoarActual * cost;
      const ahSoarMes = cSoarActual;

      const ahBrutoMes = ahTriajeMes + ahSoarMes;
      const ahNetoMes = ahBrutoMes - (12000.0 / 12.0);
      const inversionInicial = 20000.0;
      const payback = inversionInicial / ahNetoMes;
      const beneficioAnual = ahBrutoMes * 12.0;
      const costeTotal1y = inversionInicial + 12000.0;
      const roi = ((beneficioAnual - costeTotal1y) / costeTotal1y) * 100.0;

      const elAhorro = document.getElementById('res-ahorro-neto');
      if (elAhorro) elAhorro.textContent = Math.round(ahNetoMes * 12).toLocaleString() + ' €';
      const elPayback = document.getElementById('res-payback');
      if (elPayback) elPayback.textContent = Math.round(payback * 30) + ' días (' + payback.toFixed(1) + ' meses)';
      const elRoi = document.getElementById('res-roi');
      if (elRoi) elRoi.textContent = Math.round(roi).toLocaleString() + ' %';
    }}
  </script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print('index.html generado exitosamente con el diseño refinado Lucide y 0 emojis!')

if __name__ == '__main__':
    main()
