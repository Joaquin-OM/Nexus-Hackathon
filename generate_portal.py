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
    p2_count = sum(1 for n in data.get('notifications', []) if n.get('priority') == 'P2')
    p3_count = sum(1 for n in data.get('notifications', []) if n.get('priority') == 'P3')
    p4_count = sum(1 for n in data.get('notifications', []) if n.get('priority') == 'P4')
    unack_count = sum(1 for n in data.get('notifications', []) if not n.get('acknowledged'))

    html_content = f"""<!DOCTYPE html>
<html lang="es" class="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv='Cache-Control' content='no-cache, no-store, must-revalidate'>
  <meta http-equiv='Pragma' content='no-cache'>
  <meta http-equiv='Expires' content='0'>
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
    }};
  </script>
</head>
<body class="bg-[#F8FAFC] dark:bg-[#0B1118] text-slate-800 dark:text-slate-200 antialiased min-h-screen flex flex-col font-sans">

  <!-- =========================================================================
       SIDEBAR LATERAL (REORGANIZACIÓN OPERATIVA SAMPOL)
       ========================================================================= -->
  <aside id="main-sidebar" class="fixed inset-y-0 left-0 z-40 w-64 max-w-[80vw] bg-white dark:bg-[#111A24] border-r border-[#E2E8F0] dark:border-[#1E293B] flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 -translate-x-full">
    
    <!-- CABECERA DE MARCA SAMPOL -->
    <div class="px-5 py-4 border-b border-[#E2E8F0] dark:border-[#1E293B] flex items-center justify-between">
      <div class="flex items-center space-x-2.5">
        <img src="./assets/brand/sampol_logo_color.png" alt="SAMPOL" class="h-6 w-auto block dark:hidden">
        <img src="./assets/brand/sampol_logo_blanco.png" alt="SAMPOL" class="h-6 w-auto hidden dark:block">
        <div class="h-4 w-px bg-slate-300 dark:bg-slate-700"></div>
        <div>
          <span class="text-xs font-bold text-slate-900 dark:text-white tracking-tight">NEXUS SOC</span>
          <span class="block text-[9px] text-[#0784B7] dark:text-[#38BDF8] font-semibold tracking-wider">OPERATIONS 2.0</span>
        </div>
      </div>
      <button onclick="toggleSidebar()" class="md:hidden text-slate-400 hover:text-slate-600 dark:hover:text-white" aria-label="Cerrar navegación">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
    </div>

    <!-- NAVEGACIÓN AGRUPADA POR JERARQUÍA OPERATIVA -->
    <div class="flex-1 overflow-y-auto px-3 py-3 space-y-4 text-xs">
      
      <!-- BLOQUE 1: OPERACIONES -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Operaciones</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-resumen')" id="btn-tab-resumen" class="sidebar-nav-item w-full text-left active">
            <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
            <span class="flex-1">Dashboard</span>
          </button>
          <button onclick="switchTab('tab-incidentes')" id="btn-tab-incidentes" class="sidebar-nav-item w-full text-left">
            <i data-lucide="siren" class="w-4 h-4"></i>
            <span class="flex-1">Incidentes</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border border-rose-200 dark:border-rose-900">{p1_count} P1</span>
          </button>
          <button onclick="switchTab('tab-dataset')" id="btn-tab-dataset" class="sidebar-nav-item w-full text-left">
            <i data-lucide="shield-alert" class="w-4 h-4"></i>
            <span class="flex-1">Alertas</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">{total_alerts}</span>
          </button>
          <button onclick="switchTab('tab-forense')" id="btn-tab-forense" class="sidebar-nav-item w-full text-left">
            <i data-lucide="network" class="w-4 h-4"></i>
            <span class="flex-1">Investigación</span>
          </button>
          <button onclick="switchTab('tab-notifications')" id="btn-tab-notifications" class="sidebar-nav-item w-full text-left">
            <i data-lucide="bell" class="w-4 h-4"></i>
            <span class="flex-1">Notificaciones</span>
          </button>
        </div>
      </div>

      <!-- BLOQUE 2: INFRAESTRUCTURA -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Infraestructura</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-activos')" id="btn-tab-activos" class="sidebar-nav-item w-full text-left">
            <i data-lucide="server" class="w-4 h-4"></i>
            <span class="flex-1">Activos</span>
          </button>
          <button onclick="switchTab('tab-usuarios')" id="btn-tab-usuarios" class="sidebar-nav-item w-full text-left">
            <i data-lucide="users" class="w-4 h-4"></i>
            <span class="flex-1">Usuarios</span>
          </button>
          <button onclick="switchTab('tab-soar')" id="btn-tab-soar" class="sidebar-nav-item w-full text-left">
            <i data-lucide="shield-check" class="w-4 h-4"></i>
            <span class="flex-1">Respuesta</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">{soar_count}</span>
          </button>
          <button onclick="switchTab('tab-automations')" id="btn-tab-automations" class="sidebar-nav-item w-full text-left">
            <i data-lucide="workflow" class="w-4 h-4"></i>
            <span class="flex-1">Automatizaciones</span>
          </button>
        </div>
      </div>

      <!-- BLOQUE 3: ANÁLISIS Y CONTROL -->
      <div>
        <div class="px-2 mb-1.5 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Análisis y Control</div>
        <div class="space-y-0.5">
          <button onclick="switchTab('tab-informes')" id="btn-tab-informes" class="sidebar-nav-item w-full text-left">
            <i data-lucide="file-text" class="w-4 h-4"></i>
            <span class="flex-1">Informes</span>
          </button>
          <button onclick="switchTab('tab-roi')" id="btn-tab-roi" class="sidebar-nav-item w-full text-left">
            <i data-lucide="chart-line" class="w-4 h-4"></i>
            <span class="flex-1">Finanzas</span>
          </button>
          <button onclick="switchTab('tab-auditoria')" id="btn-tab-auditoria" class="sidebar-nav-item w-full text-left">
            <i data-lucide="clipboard-list" class="w-4 h-4"></i>
            <span class="flex-1">Auditoría</span>
          </button>
          <button onclick="switchTab('tab-configuracion')" id="btn-tab-configuracion" class="sidebar-nav-item w-full text-left">
            <i data-lucide="settings" class="w-4 h-4"></i>
            <span class="flex-1">Configuración</span>
          </button>
        </div>
      </div>

    </div>

    <!-- PIE DEL SIDEBAR: ESTADO SENSOR -->
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
  <div class="flex-1 md:pl-64 flex flex-col min-h-screen min-w-0 w-full max-w-full overflow-x-clip">

    <!-- HEADER SUPERIOR -->
    <header class="sticky top-0 z-20 bg-white/95 dark:bg-[#111A24]/95 backdrop-blur-sm border-b border-[#E2E8F0] dark:border-[#1E293B] px-3 sm:px-6 py-2.5 flex items-center justify-between gap-2 sm:gap-4 min-w-0 w-full">

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
    <aside id="bell-drawer" class="fixed top-14 right-2 sm:right-4 w-88 max-w-[calc(100vw-1.5rem)] max-h-[80vh] overflow-y-auto bg-white dark:bg-[#111A24] border border-[#E2E8F0] dark:border-[#1E293B] rounded-lg shadow-lg p-4 z-50 hidden space-y-3">
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
        <button onclick="switchTab('tab-incidentes'); toggleBellDrawer();" class="text-xs text-[#0784B7] dark:text-[#38BDF8] font-semibold hover:underline">
          Ver todos los incidentes →
        </button>
      </div>
    </aside>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="flex-1 p-3.5 sm:p-5 lg:p-6 max-w-7xl w-full mx-auto space-y-6 min-w-0">

      <!-- =====================================================================
           TAB 1: DASHBOARD OPERATIVO (CENTRADÍSIMO EN INCIDENTES)
           ===================================================================== -->
      <section id="tab-resumen" class="tab-content min-w-0 w-full space-y-5">

        <!-- CABECERA DE OPERACIONES -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Dashboard</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Estado de seguridad y gestión de incidentes en tiempo real.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <select class="px-2.5 py-1 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-medium focus:outline-none focus:border-[#0784B7]">
              <option>Hoy (Últimas 24h)</option>
              <option>Últimos 7 días</option>
              <option>Mes actual</option>
            </select>
            <span class="text-[11px] px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-medium flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              alertas-soc-1 · En vivo
            </span>
            <button onclick="location.reload()" class="btn-sampol-secondary text-xs" title="Actualizar datos">
              <i data-lucide="rotate-cw" class="w-3.5 h-3.5"></i>
              <span class="hidden sm:inline">Actualizar</span>
            </button>
          </div>
        </div>

        <!-- 1. BLOQUE PRINCIPAL: INCIDENTES PRIORITARIOS (ATENCIÓN INMEDIATA) -->
        <div class="sampol-card p-4 space-y-3 border-l-4 border-l-[#DC2626]">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
            <div class="flex items-center gap-2">
              <i data-lucide="siren" class="w-4 h-4 text-rose-600"></i>
              <h2 class="text-sm font-bold text-slate-900 dark:text-white">Incidentes Prioritarios (Atención Requerida)</h2>
              <span class="px-2 py-0.2 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800">{p1_count} Críticos P1</span>
            </div>
            <button onclick="switchTab('tab-incidentes')" class="text-xs text-[#0784B7] dark:text-[#38BDF8] font-semibold hover:underline flex items-center gap-1">
              Ver todos los incidentes ({notif_count}) <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
            </button>
          </div>
          
          <div id="dashboard-priority-incidents" class="space-y-2.5">
            <!-- Inyección JS con incidentes prioritarios -->
          </div>
        </div>

        <!-- 2. SEGUNDO BLOQUE: INDICADORES OPERATIVOS COMPACTOS (CLICABLES) -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">

          <div onclick="switchTab('tab-incidentes'); setIncFilter('all');" class="sampol-card p-3 cursor-pointer hover:border-[#0784B7] transition">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Incidentes Abiertos</div>
            <div class="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{notif_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">En supervisión</div>
          </div>

          <div onclick="switchTab('tab-incidentes'); setIncFilter('P1');" class="sampol-card p-3 cursor-pointer hover:border-rose-400 transition bg-rose-50/20 dark:bg-rose-950/10">
            <div class="text-[11px] font-medium text-rose-600 dark:text-rose-400">Críticos P1</div>
            <div class="text-xl font-bold text-rose-600 dark:text-rose-400 mt-0.5">{p1_count}</div>
            <div class="text-[10px] text-rose-500 mt-0.5">SLA 15 minutos</div>
          </div>

          <div onclick="switchTab('tab-incidentes'); setIncFilter('unack');" class="sampol-card p-3 cursor-pointer hover:border-amber-400 transition">
            <div class="text-[11px] font-medium text-amber-600 dark:text-amber-400">Sin Reconocer</div>
            <div id="stat-unack-dashboard" class="text-xl font-bold text-amber-600 dark:text-amber-400 mt-0.5">{unack_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Requieren acuse</div>
          </div>

          <div onclick="switchTab('tab-incidentes'); setIncFilter('unassigned');" class="sampol-card p-3 cursor-pointer hover:border-[#0784B7] transition">
            <div class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Sin Responsable</div>
            <div class="text-xl font-bold text-slate-700 dark:text-slate-300 mt-0.5">4</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Pendiente asignación</div>
          </div>

          <div onclick="switchTab('tab-incidentes'); setIncFilter('investigating');" class="sampol-card p-3 cursor-pointer hover:border-[#0784B7] transition">
            <div class="text-[11px] font-medium text-[#0784B7] dark:text-[#38BDF8]">En Investigación</div>
            <div class="text-xl font-bold text-[#0784B7] dark:text-[#38BDF8] mt-0.5">38</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Guardia activa</div>
          </div>

          <div onclick="switchTab('tab-soar')" class="sampol-card p-3 cursor-pointer hover:border-emerald-400 transition">
            <div class="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">Contención SOAR</div>
            <div class="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{soar_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Acciones ejecutadas</div>
          </div>

        </div>

        <!-- 3. TERCER BLOQUE: ALERTAS RECIENTES RELEVANTES -->
        <div class="sampol-card p-4 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">Alertas Recientes Relevantes</h2>
              <p class="text-[11px] text-slate-400">Eventos de severidad crítica y alta recibidos por los sensores del SOC.</p>
            </div>
            <button onclick="switchTab('tab-dataset')" class="text-xs text-[#0784B7] dark:text-[#38BDF8] font-semibold hover:underline flex items-center gap-1">
              Ver centro de alertas ({total_alerts}) <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
            </button>
          </div>

          <div class="overflow-x-auto min-w-0 w-full">
            <table class="sampol-table min-w-full">
              <thead>
                <tr>
                  <th>Fecha (UTC)</th>
                  <th>Código</th>
                  <th>Gravedad</th>
                  <th>Categoría INCIBE</th>
                  <th>Activo / Usuario</th>
                  <th>Incidente Asociado</th>
                </tr>
              </thead>
              <tbody id="tbl-recent-alerts">
                <!-- Inyección JS con las 5 alertas más críticas -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- 4. CUARTO BLOQUE: ACTIVIDAD RECIENTE DEL SOC -->
        <div class="sampol-card p-4 space-y-3">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <h2 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">Actividad del SOC (Auditoría en Vivo)</h2>
            <span class="text-[10px] font-mono text-slate-400">Trazabilidad RFC 822</span>
          </div>
          <div class="space-y-2 text-xs">
            <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 flex items-start justify-between gap-3">
              <div class="space-y-0.5">
                <span class="font-semibold text-rose-600 dark:text-rose-400">Incidente P1 Escalado a Dirección:</span>
                <span class="text-slate-600 dark:text-slate-300">INC-CAMP-MORENO notificado a dirti@sampol.com conforme a SLA de 15m.</span>
                <div class="text-[10px] text-slate-400 font-mono">Actor: SLA_DAEMON · Ref: SOL-B-014</div>
              </div>
              <span class="font-mono text-[10px] text-slate-400 shrink-0">19:14 UTC</span>
            </div>
            <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 flex items-start justify-between gap-3">
              <div class="space-y-0.5">
                <span class="font-semibold text-purple-600 dark:text-purple-400">Acción SOAR Ejecutada:</span>
                <span class="text-slate-600 dark:text-slate-300">Aislamiento autónomo de cuenta 'dmoreno@sampol.com' bajo Directriz 1.</span>
                <div class="text-[10px] text-slate-400 font-mono">Actor: AUTOBLOCK_ENGINE · HTTP 201 OK</div>
              </div>
              <span class="font-mono text-[10px] text-slate-400 shrink-0">19:06 UTC</span>
            </div>
            <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 flex items-start justify-between gap-3">
              <div class="space-y-0.5">
                <span class="font-semibold text-[#0784B7] dark:text-[#38BDF8]">Alerta Ingerida:</span>
                <span class="text-slate-600 dark:text-slate-300">Sensor Outlook procesó mensaje PHISH-EXT-036 con hash forense SHA-256.</span>
                <div class="text-[10px] text-slate-400 font-mono">Actor: GRAPH_DAEMON · Buzón corporativo</div>
              </div>
              <span class="font-mono text-[10px] text-slate-400 shrink-0">18:05 UTC</span>
            </div>
          </div>
        </div>

        <!-- 5. QUINTO BLOQUE: ESTADO GENERAL (GRÁFICOS SECUNDARIOS) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 min-w-0 w-full">
          <div class="sampol-card p-4 lg:col-span-2 min-w-0">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-xs font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wider">Categorías INCIBE</h2>
              <span class="text-[11px] text-slate-400">10 clases oficiales</span>
            </div>
            <div class="chart-container min-w-0">
              <canvas id="chart-incibe"></canvas>
            </div>
          </div>

          <div class="sampol-card p-4 min-w-0">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-xs font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wider">Gravedad</h2>
              <span class="text-[11px] text-slate-400">Triaje</span>
            </div>
            <div class="chart-container flex items-center justify-center min-w-0">
              <canvas id="chart-severity"></canvas>
            </div>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 2: GESTIÓN DE INCIDENTES (NUEVA PÁGINA CENTRAL)
           ===================================================================== -->
      <section id="tab-incidentes" class="tab-content hidden min-w-0 w-full space-y-4">

        <!-- CABECERA DE INCIDENTES -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Incidentes</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Gestión operativa, asignación y seguimiento de casos de ciberseguridad.</p>
          </div>
          <div class="flex items-center gap-2">
            <!-- VISTA TABLA / KANBAN -->
            <div class="inline-flex rounded-md shadow-sm" role="group">
              <button onclick="setIncidentView('table')" id="btn-view-table" class="px-3 py-1 text-xs font-medium rounded-l border border-slate-300 dark:border-slate-700 bg-[#0784B7] text-white">
                Tabla
              </button>
              <button onclick="setIncidentView('kanban')" id="btn-view-kanban" class="px-3 py-1 text-xs font-medium rounded-r border border-l-0 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50">
                Kanban
              </button>
            </div>
          </div>
        </div>

        <!-- FILTROS DE INCIDENTES -->
        <div class="sampol-card p-3 space-y-2.5">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-1.5 text-xs">
              <button onclick="setIncFilter('all')" id="btn-inc-all" class="px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium">Todos ({notif_count})</button>
              <button onclick="setIncFilter('P1')" id="btn-inc-P1" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">P1 Críticos ({p1_count})</button>
              <button onclick="setIncFilter('P2')" id="btn-inc-P2" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">P2 Altos ({p2_count})</button>
              <button onclick="setIncFilter('unack')" id="btn-inc-unack" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">Sin Reconocer</button>
              <button onclick="setIncFilter('investigating')" id="btn-inc-investigating" class="px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50">En Investigación</button>
            </div>
            <div class="w-full sm:w-64 min-w-0">
              <input type="text" id="inc-search" oninput="renderIncidentsTable()" placeholder="Buscar por ID, usuario, activo..." class="w-full px-2.5 py-1 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
            </div>
          </div>
        </div>

        <!-- VISTA TABLA (ESCRITORIO + TARJETAS MÓVILES) -->
        <div id="incidents-table-view" class="sampol-card overflow-hidden min-w-0 w-full">
          <div class="hidden md:block overflow-x-auto max-h-[600px] min-w-0 w-full">
            <table class="sampol-table min-w-full">
              <thead class="sticky top-0 z-10">
                <tr>
                  <th>ID Incidente</th>
                  <th>Título / Vector</th>
                  <th>Prioridad</th>
                  <th>Estado</th>
                  <th>Activo Afectado</th>
                  <th>Usuario</th>
                  <th>Alertas</th>
                  <th>Responsable</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody id="tbl-incidents" class="divide-y divide-slate-100 dark:divide-slate-800">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>

          <!-- MÓVIL: TARJETAS ADAPTATIVAS -->
          <div id="cards-incidents" class="block md:hidden p-3 space-y-2.5 max-h-[600px] overflow-y-auto min-w-0">
            <!-- Inyección JS -->
          </div>
        </div>

        <!-- VISTA KANBAN (COLUMNAS DE FLUJO OPERATIVO) -->
        <div id="incidents-kanban-view" class="hidden grid grid-cols-1 md:grid-cols-4 gap-3 min-w-0 w-full">
          
          <!-- COL 1: NUEVOS / TRIAJE -->
          <div class="sampol-card p-3 space-y-2.5 bg-slate-50/50 dark:bg-slate-900/30">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 dark:border-slate-700">
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Nuevos / Triaje</span>
              <span id="kanban-count-new" class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">0</span>
            </div>
            <div id="kanban-col-new" class="space-y-2 min-h-[200px]"></div>
          </div>

          <!-- COL 2: EN INVESTIGACIÓN -->
          <div class="sampol-card p-3 space-y-2.5 bg-slate-50/50 dark:bg-slate-900/30">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 dark:border-slate-700">
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200">En Investigación</span>
              <span id="kanban-count-investigating" class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">0</span>
            </div>
            <div id="kanban-col-investigating" class="space-y-2 min-h-[200px]"></div>
          </div>

          <!-- COL 3: CONTENIDOS SOAR -->
          <div class="sampol-card p-3 space-y-2.5 bg-slate-50/50 dark:bg-slate-900/30">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 dark:border-slate-700">
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Contenidos SOAR</span>
              <span id="kanban-count-contained" class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">0</span>
            </div>
            <div id="kanban-col-contained" class="space-y-2 min-h-[200px]"></div>
          </div>

          <!-- COL 4: RESUELTOS -->
          <div class="sampol-card p-3 space-y-2.5 bg-slate-50/50 dark:bg-slate-900/30">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 dark:border-slate-700">
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Resueltos / Cerrados</span>
              <span id="kanban-count-resolved" class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">0</span>
            </div>
            <div id="kanban-col-resolved" class="space-y-2 min-h-[200px]"></div>
          </div>

        </div>

      </section>

      <!-- =====================================================================
           TAB 3: ALERTAS (DATASET COMPLETO)
           ===================================================================== -->
      <section id="tab-dataset" class="tab-content hidden min-w-0 w-full space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Alertas</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Triaje e inspección bajo taxonomía oficial INCIBE ({total_alerts} únicas).</p>
          </div>
          <div class="w-full sm:w-72 min-w-0">
            <input type="text" id="alert-search" oninput="filterAlerts()" placeholder="Filtrar por código, usuario..." class="w-full px-3 py-1.5 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <div class="sampol-card overflow-hidden min-w-0 w-full">
          <!-- VISTA ESCRITORIO Y TABLET -->
          <div class="hidden md:block overflow-x-auto max-h-[580px] min-w-0 w-full">
            <table class="sampol-table min-w-full">
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

          <!-- VISTA MÓVIL: TARJETAS ADAPTATIVAS -->
          <div id="cards-alerts" class="block md:hidden p-3 space-y-2.5 max-h-[580px] overflow-y-auto min-w-0">
            <!-- Inyección JS -->
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 4: INVESTIGACIÓN (KILL CHAIN FORENSE)
           ===================================================================== -->
      <section id="tab-forense" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Investigación</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Análisis pericial de la Kill Chain, paciente cero y reducción de dwell time.</p>
        </div>

        <!-- ETAPAS -->
        <div class="sampol-card p-4 space-y-2.5 text-xs">
          <div class="font-semibold text-slate-800 dark:text-slate-200 mb-2">Cronología del Incidente (MITRE ATT&CK)</div>

          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 min-w-0 break-words">
            <span><strong>1. Phishing:</strong> AL-20261030-0025 recibido en buzón de jmoreno@sampol.com.</span>
            <span class="font-mono text-[10px] text-slate-400 shrink-0">02:41 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 min-w-0 break-words">
            <span><strong>2. Password Spray:</strong> AL-20261030-0026 detecta 43 autenticaciones anómalas.</span>
            <span class="font-mono text-[10px] text-slate-400 shrink-0">02:54 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-rose-200 dark:border-rose-900 bg-rose-50/40 dark:bg-rose-950/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 min-w-0 break-words">
            <span class="text-rose-700 dark:text-rose-300"><strong>3. Paciente Cero:</strong> Emisión ilegítima de token para jmoreno@sampol.com.</span>
            <span class="font-mono text-[10px] text-rose-600 font-bold shrink-0">03:20 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 min-w-0 break-words">
            <span><strong>4. Exfiltración:</strong> Lectura y modificación de ficheros en srv-barcelona-201.</span>
            <span class="font-mono text-[10px] text-slate-400 shrink-0">03:33 UTC</span>
          </div>
          <div class="p-2.5 rounded border border-rose-300 dark:border-rose-800 bg-rose-100/40 dark:bg-rose-950/40 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 min-w-0 break-words">
            <span class="text-rose-800 dark:text-rose-200"><strong>5. Canal C2:</strong> Balizamiento hacia sync-gateway.invalid (Precursor Ransomware).</span>
            <span class="font-mono text-[10px] text-rose-700 font-bold shrink-0">03:46 UTC</span>
          </div>
        </div>

        <!-- IOCS -->
        <div class="sampol-card p-4 min-w-0 w-full overflow-hidden">
          <div class="font-semibold text-slate-800 dark:text-slate-200 text-xs mb-3">Indicadores de Compromiso (IoCs)</div>
          <div class="overflow-x-auto min-w-0 w-full">
            <table class="sampol-table min-w-full">
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
        </div>

      </section>

      <!-- =====================================================================
           TAB 5: NOTIFICACIONES (MOTOR ANTI-FATIGA)
           ===================================================================== -->
      <section id="tab-notifications" class="tab-content hidden min-w-0 w-full space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Notificaciones</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Gestión de avisos inteligentes y anti-fatiga (capacidad 200.000 alertas/día).</p>
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
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 text-xs min-w-0">
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
          <div class="w-full sm:w-64 min-w-0">
            <input type="text" id="notif-search" oninput="renderNotifsTable()" placeholder="Buscar por usuario, ID..." class="w-full px-2.5 py-1 text-xs rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <!-- LISTA -->
        <div id="notifs-container" class="space-y-2.5">
          <!-- Inyección JS -->
        </div>

      </section>

      <!-- =====================================================================
           TAB 6: ACTIVOS
           ===================================================================== -->
      <section id="tab-activos" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Activos</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Sistemas e infraestructura crítica bajo supervisión activa.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs min-w-0 w-full">
          <div class="sampol-card p-4 space-y-2.5">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Servidores de Aplicación y Datos</div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">srv-barcelona-201</div>
                <div class="text-[10px] text-slate-400">Sede Barcelona · Servidor de Proyectos</div>
              </div>
              <span class="badge-critical">Comprometido</span>
            </div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">gw-bilbao-204</div>
                <div class="text-[10px] text-slate-400">Sede Bilbao · Gateway Perimetral</div>
              </div>
              <span class="badge-high">Contenido</span>
            </div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <div>
                <div class="font-semibold text-slate-800 dark:text-slate-200">srv-palma-205</div>
                <div class="text-[10px] text-slate-400">Sede Palma Central · Servidor Principal</div>
              </div>
              <span class="badge-low">Protegido</span>
            </div>
          </div>

          <div class="sampol-card p-4 space-y-2.5">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Políticas de Red y Segmentación OT</div>
            <div class="p-2 rounded border border-emerald-200 dark:border-emerald-900 bg-emerald-50/30 dark:bg-emerald-950/20">
              <div class="font-medium text-emerald-800 dark:text-emerald-300">Plantas de Cogeneración & Aeropuertos</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Exclusión estricta en lista blanca SOAR. Toda contención exige supervisión humana.</div>
            </div>
            <div class="p-2 rounded border border-slate-200 dark:border-slate-700">
              <div class="font-medium text-slate-700 dark:text-slate-300">Buzón de Operaciones SOC</div>
              <div class="text-[10px] text-slate-400 mt-0.5">equipo_1_hackaton@sampol.com protegido contra bloqueos autónomos.</div>
            </div>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 7: USUARIOS (DIRECTORIO DE IDENTIDADES)
           ===================================================================== -->
      <section id="tab-usuarios" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Usuarios</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Supervisión de cuentas corporativas, privilegios y estado de contención.</p>
        </div>

        <div class="sampol-card overflow-hidden min-w-0 w-full">
          <div class="overflow-x-auto min-w-0 w-full">
            <table class="sampol-table min-w-full">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Departamento</th>
                  <th>Sede</th>
                  <th>Estado Identidad</th>
                  <th>Incidentes Asociados</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="font-mono font-bold text-rose-600">jmoreno@sampol.com</td>
                  <td>Ingeniería de Proyectos</td>
                  <td>Barcelona</td>
                  <td><span class="badge-critical">Bloqueado (SOAR)</span></td>
                  <td>INC-CAMP-MORENO</td>
                  <td><button onclick="switchTab('tab-soar')" class="btn-sampol-secondary text-[10px] py-1">Ver Contención</button></td>
                </tr>
                <tr>
                  <td class="font-mono font-bold text-rose-600">bmoreno@sampol.com</td>
                  <td>Operaciones</td>
                  <td>Bilbao</td>
                  <td><span class="badge-critical">Bloqueado (SOAR)</span></td>
                  <td>INC-USR-bmoreno</td>
                  <td><button onclick="switchTab('tab-soar')" class="btn-sampol-secondary text-[10px] py-1">Ver Contención</button></td>
                </tr>
                <tr>
                  <td class="font-mono font-bold text-rose-600">cmoreno@sampol.com</td>
                  <td>Sistemas</td>
                  <td>Madrid</td>
                  <td><span class="badge-critical">Bloqueado (SOAR)</span></td>
                  <td>INC-USR-cmoreno</td>
                  <td><button onclick="switchTab('tab-soar')" class="btn-sampol-secondary text-[10px] py-1">Ver Contención</button></td>
                </tr>
                <tr>
                  <td class="font-mono font-medium text-slate-900 dark:text-white">director.ti@sampol.com</td>
                  <td>Dirección de Tecnología</td>
                  <td>Palma</td>
                  <td><span class="badge-low">Protegido (VIP)</span></td>
                  <td>-</td>
                  <td><span class="text-[11px] text-slate-400">Whitelist Activa</span></td>
                </tr>
                <tr>
                  <td class="font-mono font-medium text-slate-900 dark:text-white">guardia_soc@sampol.com</td>
                  <td>Centro de Ciberseguridad</td>
                  <td>Palma</td>
                  <td><span class="badge-low">Activo (SOC)</span></td>
                  <td>-</td>
                  <td><span class="text-[11px] text-slate-400">Superintendente</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 8: RESPUESTA (SOAR - DIRECTRIZ 1)
           ===================================================================== -->
      <section id="tab-soar" class="tab-content hidden min-w-0 w-full space-y-4">
        
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Respuesta</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Contención autónoma perimetral (Directriz 1 - 18:00).</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            {soar_count} Acciones Ejecutadas
          </span>
        </div>

        <div class="sampol-card overflow-hidden min-w-0 w-full">
          <!-- VISTA ESCRITORIO Y TABLET -->
          <div class="hidden md:block overflow-x-auto max-h-[500px] min-w-0 w-full">
            <table class="sampol-table min-w-full">
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

          <!-- VISTA MÓVIL: TARJETAS ADAPTATIVAS -->
          <div id="cards-soar" class="block md:hidden p-3 space-y-2.5 max-h-[500px] overflow-y-auto min-w-0">
            <!-- Inyección JS -->
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 9: AUTOMATIZACIONES
           ===================================================================== -->
      <section id="tab-automations" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Automatizaciones</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Pipelines de ingesta continua y contención perimetral.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs min-w-0 w-full">
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
           TAB 10: INFORMES & COMPLIANCE NIS2
           ===================================================================== -->
      <section id="tab-informes" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Informes</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Generación y consulta de expedientes de ciberseguridad y pre-notificaciones NIS2.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 text-xs min-w-0 w-full">
          <div class="sampol-card p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900 dark:text-white">Pre-notificación NIS2</span>
              <span class="badge-low">24h Cumplida</span>
            </div>
            <p class="text-slate-500 text-[11px]">Plantilla oficial remitida a INCIBE-CERT bajo el Artículo 23 de la Directiva Europea NIS2.</p>
            <div class="pt-2">
              <span class="text-[#0784B7] dark:text-[#38BDF8] font-semibold text-[11px]">PRENOTIFICACION_INCIDENTE_NIS2.docx</span>
            </div>
          </div>

          <div class="sampol-card p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900 dark:text-white">Informe Forense Kill Chain</span>
              <span class="badge-low">Pericial</span>
            </div>
            <p class="text-slate-500 text-[11px]">Reconstrucción cronológica de accesos, paciente cero y contención de C2.</p>
            <div class="pt-2">
              <span class="text-[#0784B7] dark:text-[#38BDF8] font-semibold text-[11px]">INFORME_FORENSE_KILL_CHAIN.docx</span>
            </div>
          </div>

          <div class="sampol-card p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900 dark:text-white">Memoria de Industrialización</span>
              <span class="badge-low">Aprobada</span>
            </div>
            <p class="text-slate-500 text-[11px]">Plan estratégico de pase a producción de NEXUS SOC 2.0 para Grupo SAMPOL.</p>
            <div class="pt-2">
              <span class="text-[#0784B7] dark:text-[#38BDF8] font-semibold text-[11px]">PLAN_INDUSTRIALIZACION_NEXUS.docx</span>
            </div>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 11: FINANZAS (CALCULADORA DE RETORNO Y ROI DEL DIRECTOR)
           ===================================================================== -->
      <section id="tab-roi" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Finanzas</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Retorno de inversión, ahorro operativo y comparativa económica (Directorio TI).</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 min-w-0 w-full">

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
           TAB 12: AUDITORÍA
           ===================================================================== -->
      <section id="tab-auditoria" class="tab-content hidden min-w-0 w-full space-y-4">

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

      <!-- =====================================================================
           TAB 13: CONFIGURACIÓN
           ===================================================================== -->
      <section id="tab-configuracion" class="tab-content hidden min-w-0 w-full space-y-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Configuración</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Parámetros operativos, umbrales de SLA y reglas de Lista Blanca.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs min-w-0 w-full">
          <div class="sampol-card p-4 space-y-3">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Umbrales de SLA y Cooldown</div>
            <div class="space-y-2">
              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span class="text-slate-600 dark:text-slate-400">SLA Incidentes Críticos (P1):</span>
                <span class="font-semibold text-rose-600">15 minutos</span>
              </div>
              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span class="text-slate-600 dark:text-slate-400">SLA Incidentes Altos (P2):</span>
                <span class="font-semibold text-amber-600">60 minutos</span>
              </div>
              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span class="text-slate-600 dark:text-slate-400">Ventana de Cooldown Anti-Fatiga:</span>
                <span class="font-semibold text-[#0784B7]">15 minutos</span>
              </div>
              <div class="flex justify-between items-center py-1">
                <span class="text-slate-600 dark:text-slate-400">Frecuencia Sondeo Graph API:</span>
                <span class="font-semibold text-emerald-600">45 segundos</span>
              </div>
            </div>
          </div>

          <div class="sampol-card p-4 space-y-3">
            <div class="font-semibold text-slate-800 dark:text-slate-200">Salvaguardas de Lista Blanca (Directriz 1)</div>
            <p class="text-slate-500 text-[11px]">Entidades permanentemente exentas de auto-bloqueo para evitar disrupción de servicios críticos.</p>
            <div class="space-y-1.5 font-mono text-[11px]">
              <div class="p-1.5 rounded bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300">✓ director.ti@sampol.com (VIP_DIRECCION)</div>
              <div class="p-1.5 rounded bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300">✓ equipo_1_hackaton@sampol.com (BUZON_SOC)</div>
              <div class="p-1.5 rounded bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300">✓ 192.168.10.0/24 (RED_PLANTA_OT)</div>
            </div>
          </div>
        </div>

      </section>

    </main>

  </div>

  <!-- =========================================================================
       MODAL DE DETALLE Y GESTIÓN DE INCIDENTE
       ========================================================================= -->
  <div id="incident-modal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden flex items-center justify-center p-3 sm:p-4">
    <div class="bg-white dark:bg-[#111A24] border border-[#E2E8F0] dark:border-[#1E293B] rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-4 p-5 min-w-0">
      
      <!-- CABECERA MODAL -->
      <div class="flex items-start justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div>
          <div class="flex items-center gap-2">
            <span id="modal-inc-id" class="font-mono text-sm font-bold text-[#0784B7] dark:text-[#38BDF8]">INC-ID</span>
            <span id="modal-inc-priority" class="badge-critical">P1</span>
            <span id="modal-inc-status" class="badge-low">Activo</span>
          </div>
          <h2 id="modal-inc-title" class="text-base font-bold text-slate-900 dark:text-white mt-1">Título del Incidente</h2>
        </div>
        <button onclick="closeIncidentModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white p-1">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- DETALLES DEL IMPACTO -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Activo Afectado</div>
          <div id="modal-inc-asset" class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Usuario</div>
          <div id="modal-inc-user" class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Alertas Agrupadas</div>
          <div id="modal-inc-count" class="font-semibold text-[#0784B7] dark:text-[#38BDF8] mt-0.5">1</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Score de Riesgo</div>
          <div id="modal-inc-score" class="font-bold text-rose-600 mt-0.5">100 / 100</div>
        </div>
      </div>

      <!-- DESCRIPCIÓN TÉCNICA -->
      <div class="space-y-1 text-xs">
        <strong class="text-slate-700 dark:text-slate-300">Descripción y Evidencia</strong>
        <p id="modal-inc-desc" class="p-3 rounded bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 font-mono text-[11px] leading-relaxed break-words"></p>
      </div>

      <!-- FACTORES DE CORRELACIÓN -->
      <div class="space-y-1 text-xs">
        <strong class="text-slate-700 dark:text-slate-300">Factores Correlacionados por el Motor</strong>
        <div id="modal-inc-reasons" class="flex flex-wrap gap-1.5 pt-1"></div>
      </div>

      <!-- ASIGNACIÓN DE RESPONSABLE -->
      <div class="p-3 rounded bg-slate-50 dark:bg-slate-800/50 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div>
          <span class="font-semibold text-slate-700 dark:text-slate-300">Responsable Asignado:</span>
          <span id="modal-inc-responsible" class="ml-1 text-[#0784B7] font-medium">guardia_soc@sampol.com</span>
        </div>
        <div class="flex items-center gap-2">
          <select id="modal-select-assignee" class="px-2 py-1 text-xs rounded bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200">
            <option value="guardia_soc@sampol.com">guardia_soc@sampol.com</option>
            <option value="analista_l2@sampol.com">analista_l2@sampol.com</option>
            <option value="director.ti@sampol.com">director.ti@sampol.com</option>
          </select>
          <button onclick="reassignCurrentIncident()" class="btn-sampol-secondary text-xs py-1 px-2.5">Asignar</button>
        </div>
      </div>

      <!-- ACCIONES DE RESPUESTA -->
      <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
        <button id="modal-btn-ack" onclick="ackCurrentIncident()" class="btn-sampol-primary text-xs">
          <i data-lucide="check" class="w-3.5 h-3.5"></i>
          <span>Reconocer Incidente (ACK)</span>
        </button>
        <button onclick="closeIncidentModal()" class="btn-sampol-secondary text-xs">
          Cerrar
        </button>
      </div>

    </div>
  </div>

  <!-- =========================================================================
       SCRIPTS JAVASCRIPT
       ========================================================================= -->
  <script>
    const ALERTS_DATA = {alerts_json};
    const SOAR_DATA = {soar_json};
    let NOTIFS_DATA = {notifs_json};
    const METRICS_DATA = {metrics_json};

    let CURRENT_NOTIF_FILTER = 'all';
    let CURRENT_INC_FILTER = 'all';
    let CURRENT_INC_VIEW = 'table';
    let CURRENT_MODAL_INC_ID = null;

    const TAB_NAMES = {{
      'tab-resumen': 'Dashboard',
      'tab-incidentes': 'Incidentes',
      'tab-dataset': 'Alertas',
      'tab-forense': 'Investigación',
      'tab-notifications': 'Notificaciones',
      'tab-activos': 'Activos',
      'tab-usuarios': 'Usuarios',
      'tab-soar': 'Respuesta',
      'tab-automations': 'Automatizaciones',
      'tab-informes': 'Informes',
      'tab-roi': 'Finanzas',
      'tab-auditoria': 'Auditoría',
      'tab-configuracion': 'Configuración'
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

    function toggleSidebar() {{
      const sb = document.getElementById('main-sidebar');
      const bd = document.getElementById('sidebar-backdrop');
      if (!sb || !bd) return;
      const isClosed = sb.classList.contains('-translate-x-full');
      if (isClosed) {{
        sb.classList.remove('-translate-x-full');
        bd.classList.remove('hidden');
      }} else {{
        sb.classList.add('-translate-x-full');
        bd.classList.add('hidden');
      }}
    }}

    function toggleBellDrawer() {{
      const d = document.getElementById('bell-drawer');
      if (!d) return;
      d.classList.toggle('hidden');
      if (!d.classList.contains('hidden')) {{
        renderDrawerList();
      }}
    }}

    function toggleTheme() {{
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      updateThemeIcon(isDark);
    }}

    function updateThemeIcon(isDark) {{
      const el = document.getElementById('theme-icon');
      if (!el) return;
      el.innerHTML = isDark 
        ? '<i data-lucide="sun" class="w-4 h-4"></i>' 
        : '<i data-lucide="moon" class="w-4 h-4"></i>';
      if (window.lucide) lucide.createIcons();
    }}

    function initTheme() {{
      const saved = localStorage.getItem('theme');
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = saved === 'dark' || (!saved && prefersDark);
      if (isDark) {{
        document.documentElement.classList.add('dark');
      }} else {{
        document.documentElement.classList.remove('dark');
      }}
      updateThemeIcon(isDark);
    }}

    // RENDER: DASHBOARD INCIDENTES PRIORITARIOS
    function renderDashboardPriorityIncidents() {{
      const c = document.getElementById('dashboard-priority-incidents');
      if (!c) return;
      const priorities = (NOTIFS_DATA || []).filter(n => n.priority === 'P1' || (!n.acknowledged && n.priority === 'P2')).slice(0, 4);
      if (!priorities.length) {{
        c.innerHTML = '<div class="p-4 text-center text-xs text-slate-400">No hay incidentes críticos pendientes de atención.</div>';
        return;
      }}
      c.innerHTML = priorities.map(n => {{
        const isP1 = n.priority === 'P1';
        return `
          <div class="p-3 rounded-lg border ${{isP1 ? 'border-rose-200 dark:border-rose-900 bg-rose-50/30 dark:bg-rose-950/20' : 'border-amber-200 dark:border-amber-900 bg-amber-50/30 dark:bg-amber-950/20'}} space-y-2 text-xs">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="${{isP1 ? 'badge-critical' : 'badge-high'}} font-bold">${{n.priority}}</span>
                <span class="font-mono font-bold text-slate-900 dark:text-white">${{n.incident_id}}</span>
                <span class="text-slate-400">·</span>
                <span class="text-slate-500">${{n.count}} alertas agrupadas</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-mono text-slate-500">${{n.last_event_at ? n.last_event_at.substring(11, 16) + ' UTC' : 'Reciente'}}</span>
                <button onclick="openIncidentModal(${{n.id}})" class="btn-sampol-primary text-[11px] py-1 px-2.5">
                  <span>Gestionar</span>
                  <i data-lucide="arrow-right" class="w-3 h-3"></i>
                </button>
              </div>
            </div>
            <div class="font-semibold text-slate-800 dark:text-slate-200">${{n.title}}</div>
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-500 dark:text-slate-400">
              <span><strong>Activo:</strong> ${{n.affected_asset || 'N/A'}}</span>
              <span><strong>Usuario:</strong> ${{n.affected_user || 'N/A'}}</span>
              <span><strong>Responsable:</strong> ${{n.acknowledged_by || 'Sin asignar'}}</span>
              <span class="${{isP1 ? 'text-rose-600 font-semibold' : 'text-slate-500'}}">SLA: ${{isP1 ? '15m (Crítico)' : '60m'}}</span>
            </div>
          </div>
        `;
      }}).join('');
      if (window.lucide) lucide.createIcons();
    }}

    // RENDER: ALERTAS RECIENTES EN DASHBOARD
    function renderDashboardRecentAlerts() {{
      const tb = document.getElementById('tbl-recent-alerts');
      if (!tb) return;
      tb.innerHTML = (ALERTS_DATA || []).slice(0, 5).map(a => `
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
          <td class="font-mono text-slate-400 text-[10px] whitespace-nowrap">${{a.timestamp.substring(0, 16)}}</td>
          <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-medium whitespace-nowrap">${{a.internal_id}}</td>
          <td>
            <span class="${{a.severity === 'CRITICA' ? 'badge-critical' : 'badge-high'}}">${{a.severity}}</span>
          </td>
          <td class="text-slate-700 dark:text-slate-300 font-medium">${{a.class}}</td>
          <td class="font-mono text-slate-600 dark:text-slate-400">${{a.host || a.user || '-'}}</td>
          <td class="font-mono text-xs text-slate-500 truncate max-w-xs">INC-CAMP-MORENO</td>
        </tr>
      `).join('');
    }}

    // GESTIÓN DE INCIDENTES (TABLA Y KANBAN)
    function setIncidentView(view) {{
      CURRENT_INC_VIEW = view;
      const btnTable = document.getElementById('btn-view-table');
      const btnKanban = document.getElementById('btn-view-kanban');
      const vTable = document.getElementById('incidents-table-view');
      const vKanban = document.getElementById('incidents-kanban-view');

      if (view === 'table') {{
        btnTable.className = 'px-3 py-1 text-xs font-medium rounded-l border border-slate-300 dark:border-slate-700 bg-[#0784B7] text-white';
        btnKanban.className = 'px-3 py-1 text-xs font-medium rounded-r border border-l-0 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50';
        vTable.classList.remove('hidden');
        vKanban.classList.add('hidden');
      }} else {{
        btnTable.className = 'px-3 py-1 text-xs font-medium rounded-l border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50';
        btnKanban.className = 'px-3 py-1 text-xs font-medium rounded-r border border-l-0 border-slate-300 dark:border-slate-700 bg-[#0784B7] text-white';
        vTable.classList.add('hidden');
        vKanban.classList.remove('hidden');
        renderIncidentsKanban();
      }}
      if (window.lucide) lucide.createIcons();
    }}

    function setIncFilter(filter) {{
      CURRENT_INC_FILTER = filter;
      ['all', 'P1', 'P2', 'unack', 'investigating'].forEach(f => {{
        const b = document.getElementById('btn-inc-' + f);
        if (b) {{
          b.className = f === filter
            ? 'px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium'
            : 'px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50';
        }}
      }});
      renderIncidentsTable();
      if (CURRENT_INC_VIEW === 'kanban') renderIncidentsKanban();
    }}

    function renderIncidentsTable() {{
      const q = (document.getElementById('inc-search') ? document.getElementById('inc-search').value : '').toLowerCase();
      const tb = document.getElementById('tbl-incidents');
      const cards = document.getElementById('cards-incidents');

      const filtered = (NOTIFS_DATA || []).filter(n => {{
        let matchF = true;
        if (CURRENT_INC_FILTER === 'P1') matchF = n.priority === 'P1';
        else if (CURRENT_INC_FILTER === 'P2') matchF = n.priority === 'P2';
        else if (CURRENT_INC_FILTER === 'unack') matchF = !n.acknowledged;
        else if (CURRENT_INC_FILTER === 'investigating') matchF = n.acknowledged;

        const matchQ = !q || (n.incident_id && n.incident_id.toLowerCase().includes(q)) ||
                             (n.title && n.title.toLowerCase().includes(q)) ||
                             (n.affected_user && n.affected_user.toLowerCase().includes(q)) ||
                             (n.affected_asset && n.affected_asset.toLowerCase().includes(q));
        return matchF && matchQ;
      }});

      if (tb) {{
        tb.innerHTML = filtered.map(n => {{
          const isP1 = n.priority === 'P1';
          const isP2 = n.priority === 'P2';
          const badgeClass = isP1 ? 'badge-critical' : isP2 ? 'badge-high' : 'badge-low';
          return `
            <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-bold whitespace-nowrap">${{n.incident_id}}</td>
              <td class="font-medium text-slate-900 dark:text-white max-w-xs truncate">${{n.title}}</td>
              <td><span class="${{badgeClass}}">${{n.priority}}</span></td>
              <td><span class="${{n.acknowledged ? 'badge-low' : 'badge-high'}}">${{n.acknowledged ? 'En Investigación' : 'Sin Acuse'}}</span></td>
              <td class="font-mono text-slate-600 dark:text-slate-400 whitespace-nowrap">${{n.affected_asset || '-'}}</td>
              <td class="font-mono text-slate-600 dark:text-slate-400 whitespace-nowrap">${{n.affected_user || '-'}}</td>
              <td class="font-semibold text-slate-700 dark:text-slate-300">${{n.count}}</td>
              <td class="text-slate-500 whitespace-nowrap">${{n.acknowledged_by || 'Sin asignar'}}</td>
              <td>
                <button onclick="openIncidentModal(${{n.id}})" class="btn-sampol-secondary text-[11px] py-1 px-2.5">
                  Detalle
                </button>
              </td>
            </tr>
          `;
        }}).join('');
      }}

      if (cards) {{
        cards.innerHTML = filtered.map(n => {{
          const isP1 = n.priority === 'P1';
          const badgeClass = isP1 ? 'badge-critical' : 'badge-high';
          return `
            <div class="mobile-card space-y-2 text-xs">
              <div class="flex items-center justify-between gap-2">
                <span class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-bold">${{n.incident_id}}</span>
                <span class="${{badgeClass}}">${{n.priority}}</span>
              </div>
              <div class="font-semibold text-slate-900 dark:text-white">${{n.title}}</div>
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 dark:text-slate-400">
                <span><strong>Activo:</strong> ${{n.affected_asset || '-'}}</span>
                <span><strong>Usuario:</strong> ${{n.affected_user || '-'}}</span>
                <span><strong>Alertas:</strong> ${{n.count}}</span>
              </div>
              <div class="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <span class="text-[10px] text-slate-400">Resp: ${{n.acknowledged_by || 'Sin asignar'}}</span>
                <button onclick="openIncidentModal(${{n.id}})" class="btn-sampol-primary text-[11px] py-1 px-2">
                  Gestionar
                </button>
              </div>
            </div>
          `;
        }}).join('');
      }}
      if (window.lucide) lucide.createIcons();
    }}

    function renderIncidentsKanban() {{
      const cols = {{
        new: document.getElementById('kanban-col-new'),
        investigating: document.getElementById('kanban-col-investigating'),
        contained: document.getElementById('kanban-col-contained'),
        resolved: document.getElementById('kanban-col-resolved')
      }};
      if (!cols.new) return;

      const lists = {{ new: [], investigating: [], contained: [], resolved: [] }};

      (NOTIFS_DATA || []).forEach(n => {{
        if (!n.acknowledged) {{
          lists.new.push(n);
        }} else if (n.status === 'resolved' || n.status === 'cerrado') {{
          lists.resolved.push(n);
        }} else if (n.incident_id && (n.incident_id.includes('MORENO') || n.incident_id.includes('srv') || n.risk_score >= 90)) {{
          lists.contained.push(n);
        }} else {{
          lists.investigating.push(n);
        }}
      }});

      document.getElementById('kanban-count-new').textContent = lists.new.length;
      document.getElementById('kanban-count-investigating').textContent = lists.investigating.length;
      document.getElementById('kanban-count-contained').textContent = lists.contained.length;
      document.getElementById('kanban-count-resolved').textContent = lists.resolved.length;

      const renderCard = n => `
        <div onclick="openIncidentModal(${{n.id}})" class="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/80 shadow-sm hover:border-[#0784B7] cursor-pointer space-y-1.5 transition">
          <div class="flex items-center justify-between">
            <span class="font-mono text-[10px] font-bold text-[#0784B7] dark:text-[#38BDF8]">${{n.incident_id}}</span>
            <span class="${{n.priority === 'P1' ? 'badge-critical' : 'badge-high'}} text-[9px]">${{n.priority}}</span>
          </div>
          <div class="font-semibold text-slate-800 dark:text-slate-200 text-xs line-clamp-2">${{n.title}}</div>
          <div class="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-700/60">
            <span>${{n.affected_user || n.affected_asset || '-'}}</span>
            <span>${{n.count}} al.</span>
          </div>
        </div>
      `;

      cols.new.innerHTML = lists.new.map(renderCard).join('') || '<div class="text-center py-4 text-[11px] text-slate-400">Sin nuevos casos</div>';
      cols.investigating.innerHTML = lists.investigating.map(renderCard).join('') || '<div class="text-center py-4 text-[11px] text-slate-400">Sin casos activos</div>';
      cols.contained.innerHTML = lists.contained.map(renderCard).join('') || '<div class="text-center py-4 text-[11px] text-slate-400">Sin contenciones</div>';
      cols.resolved.innerHTML = lists.resolved.map(renderCard).join('') || '<div class="text-center py-4 text-[11px] text-slate-400">Sin resolver</div>';
    }}

    // MODAL DE DETALLE DE INCIDENTE
    function openIncidentModal(id) {{
      const inc = (NOTIFS_DATA || []).find(n => n.id === id);
      if (!inc) return;
      CURRENT_MODAL_INC_ID = id;

      document.getElementById('modal-inc-id').textContent = inc.incident_id;
      document.getElementById('modal-inc-title').textContent = inc.title;
      document.getElementById('modal-inc-priority').textContent = inc.priority;
      document.getElementById('modal-inc-priority').className = inc.priority === 'P1' ? 'badge-critical' : 'badge-high';
      document.getElementById('modal-inc-status').textContent = inc.acknowledged ? 'En Investigación' : 'Sin Acuse';
      document.getElementById('modal-inc-status').className = inc.acknowledged ? 'badge-low' : 'badge-high';
      document.getElementById('modal-inc-asset').textContent = inc.affected_asset || 'Infraestructura General';
      document.getElementById('modal-inc-user').textContent = inc.affected_user || 'Sin cuenta individual';
      document.getElementById('modal-inc-count').textContent = inc.count + ' eventos consolidados';
      document.getElementById('modal-inc-score').textContent = (inc.risk_score || 85) + ' / 100';
      document.getElementById('modal-inc-desc').textContent = inc.description || 'Sin descripción adicional.';
      document.getElementById('modal-inc-responsible').textContent = inc.acknowledged_by || 'Sin asignar';

      const reasonsContainer = document.getElementById('modal-inc-reasons');
      reasonsContainer.innerHTML = (inc.reasons || []).map(r => `
        <span class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-[10px] border border-slate-200 dark:border-slate-700">
          ${{r}}
        </span>
      `).join('') || '<span class="text-slate-400 text-[10px]">Sin factores adicionales</span>';

      const btnAck = document.getElementById('modal-btn-ack');
      if (btnAck) {{
        btnAck.innerHTML = inc.acknowledged
          ? '<i data-lucide="check-check" class="w-3.5 h-3.5"></i><span>Acusado por ' + (inc.acknowledged_by || 'guardia') + '</span>'
          : '<i data-lucide="check" class="w-3.5 h-3.5"></i><span>Reconocer Incidente (ACK)</span>';
      }}

      const modal = document.getElementById('incident-modal');
      modal.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }}

    function closeIncidentModal() {{
      const modal = document.getElementById('incident-modal');
      if (modal) modal.classList.add('hidden');
      CURRENT_MODAL_INC_ID = null;
    }}

    function ackCurrentIncident() {{
      if (!CURRENT_MODAL_INC_ID) return;
      ackNotification(CURRENT_MODAL_INC_ID);
      openIncidentModal(CURRENT_MODAL_INC_ID);
    }}

    function reassignCurrentIncident() {{
      if (!CURRENT_MODAL_INC_ID) return;
      const sel = document.getElementById('modal-select-assignee');
      const val = sel ? sel.value : 'guardia_soc@sampol.com';
      NOTIFS_DATA = (NOTIFS_DATA || []).map(n => {{
        if (n.id === CURRENT_MODAL_INC_ID) {{
          return {{ ...n, acknowledged: true, acknowledged_by: val, status: 'investigating' }};
        }}
        return n;
      }});
      renderIncidentsTable();
      renderDashboardPriorityIncidents();
      renderNotifsTable();
      openIncidentModal(CURRENT_MODAL_INC_ID);
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
      renderIncidentsTable();
      renderDashboardPriorityIncidents();
    }}

    function renderDrawerList() {{
      const c = document.getElementById('drawer-notifs-list');
      if (!c) return;
      const unack = (NOTIFS_DATA || []).filter(n => !n.acknowledged && (n.priority === 'P1' || n.priority === 'P2'));
      if (!unack.length) {{
        c.innerHTML = '<p class="text-slate-400 text-center py-4">No hay avisos prioritarios pendientes.</p>';
        return;
      }}
      c.innerHTML = unack.slice(0, 8).map(n => `
        <div class="p-2.5 rounded border ${{n.priority === 'P1' ? 'border-rose-200 dark:border-rose-900 bg-rose-50/50 dark:bg-rose-950/20' : 'border-amber-200 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/20'}} space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800 dark:text-slate-100">${{n.incident_id}}</span>
            <span class="${{n.priority === 'P1' ? 'badge-critical' : 'badge-high'}} font-bold">${{n.priority}}</span>
          </div>
          <p class="text-slate-600 dark:text-slate-300 text-[11px] line-clamp-2">${{n.title}}</p>
          <div class="flex items-center justify-between pt-1">
            <span class="text-[10px] text-slate-400">${{n.count}} alertas</span>
            <button onclick="ackNotification(${{n.id}})" class="text-[10px] text-[#0784B7] dark:text-[#38BDF8] font-bold hover:underline">
              Acusar
            </button>
          </div>
        </div>
      `).join('');
      if (window.lucide) lucide.createIcons();
    }}

    function setNotifFilter(f) {{
      CURRENT_NOTIF_FILTER = f;
      ['all', 'P1', 'P2', 'unack'].forEach(id => {{
        const btn = document.getElementById('btn-nf-' + id);
        if (btn) {{
          btn.className = (id === f) 
            ? 'px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium'
            : 'px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50';
        }}
      }});
      renderNotifsTable();
    }}

    function renderNotifsTable() {{
      const q = (document.getElementById('notif-search') ? document.getElementById('notif-search').value : '').toLowerCase();
      const c = document.getElementById('notifs-container');
      if (!c) return;

      const filtered = (NOTIFS_DATA || []).filter(n => {{
        const matchF = CURRENT_NOTIF_FILTER === 'all' || 
                       (CURRENT_NOTIF_FILTER === 'unack' && !n.acknowledged) ||
                       (n.priority === CURRENT_NOTIF_FILTER);
        const matchQ = !q || (n.incident_id && n.incident_id.toLowerCase().includes(q)) || 
                             (n.title && n.title.toLowerCase().includes(q)) ||
                             (n.affected_user && n.affected_user.toLowerCase().includes(q));
        return matchF && matchQ;
      }});

      if (!filtered.length) {{
        c.innerHTML = '<div class="p-8 text-center text-slate-400 bg-white dark:bg-[#111A24] rounded-lg border border-slate-200 dark:border-slate-800 text-xs">No se encontraron notificaciones.</div>';
        return;
      }}

      c.innerHTML = filtered.map(n => {{
        const isP1 = n.priority === 'P1';
        const isP2 = n.priority === 'P2';
        const cardBorder = isP1 
          ? 'border-l-4 border-l-[#DC2626] border-slate-200 dark:border-slate-800' 
          : isP2 
          ? 'border-l-4 border-l-[#EA580C] border-slate-200 dark:border-slate-800' 
          : 'border-l-4 border-l-[#16A34A] border-slate-200 dark:border-slate-800';
        const badgeColor = isP1 ? 'badge-critical' : isP2 ? 'badge-high' : 'badge-low';

        const reasonsHtml = ((n.reasons || []).slice(0, 3)).map(r => `<span class="px-1.5 py-0.5 rounded bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[10px] border border-slate-200 dark:border-slate-700">${{r}}</span>`).join(' ');

        return `
          <div class="sampol-card p-4 ${{cardBorder}} space-y-2 text-xs">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="${{badgeColor}}">${{n.priority}}</span>
                <span class="font-mono font-bold text-slate-900 dark:text-white">${{n.incident_id}}</span>
                <span class="text-slate-400">·</span>
                <span class="text-slate-500">${{n.count}} alertas agrupadas</span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-[10px] font-mono text-slate-400">${{n.last_event_at ? n.last_event_at.substring(0, 16) : '2026-11-03'}}</span>
                ${{n.acknowledged 
                  ? '<span class="text-[10px] text-emerald-600 font-medium">Acusado por ' + (n.acknowledged_by || 'guardia') + '</span>'
                  : '<button onclick="ackNotification(' + n.id + ')" class="btn-sampol-primary text-[10px] py-1 px-2.5">Reconocer</button>'}}
              </div>
            </div>

            <div class="font-semibold text-slate-800 dark:text-slate-200 text-xs">${{n.title}}</div>
            <p class="text-slate-500 dark:text-slate-400 text-[11px] leading-relaxed">${{n.description}}</p>

            <div class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400">
              <div class="flex items-center space-x-3">
                <span>Activo: <strong class="text-slate-600 dark:text-slate-300 font-mono">${{n.affected_asset || 'N/A'}}</strong></span>
                <span>Usuario: <strong class="text-slate-600 dark:text-slate-300 font-mono">${{n.affected_user || 'N/A'}}</strong></span>
              </div>
              <div class="flex flex-wrap items-center gap-1">
                ${{reasonsHtml}}
              </div>
            </div>
          </div>
        `;
      }}).join('');

      const p1Unack = (NOTIFS_DATA || []).filter(n => n.priority === 'P1' && !n.acknowledged).length;
      const bBadge = document.getElementById('bell-badge-count');
      if (bBadge) bBadge.textContent = p1Unack;
      const stP1 = document.getElementById('stat-p1-count');
      if (stP1) stP1.textContent = p1Unack;
      const stUnack = document.getElementById('stat-unack-dashboard');
      if (stUnack) stUnack.textContent = (NOTIFS_DATA || []).filter(n => !n.acknowledged).length;
      if (window.lucide) lucide.createIcons();
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
      renderDashboardPriorityIncidents();
      renderIncidentsTable();
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
      renderDashboardPriorityIncidents();
      renderIncidentsTable();
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
      switchTab('tab-incidentes');
      const inputInc = document.getElementById('inc-search');
      if (inputInc) {{
        inputInc.value = q;
        renderIncidentsTable();
      }}
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      initTheme();
      renderDashboardPriorityIncidents();
      renderDashboardRecentAlerts();
      renderIncidentsTable();
      renderNotifsTable();
      renderDrawerList();
      calcROI();

      const tbAlerts = document.getElementById('tbl-alerts');
      if (tbAlerts) {{
        tbAlerts.innerHTML = (ALERTS_DATA || []).slice(0, 100).map(a => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
            <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-medium whitespace-nowrap">${{a.internal_id}}</td>
            <td class="text-slate-400 font-mono text-[10px] whitespace-nowrap">${{a.timestamp.substring(0, 16)}}</td>
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

      const cAlerts = document.getElementById('cards-alerts');
      if (cAlerts) {{
        cAlerts.innerHTML = (ALERTS_DATA || []).slice(0, 100).map(a => `
          <div class="mobile-card space-y-2 text-xs">
            <div class="flex items-center justify-between gap-2">
              <span class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-bold text-xs">${{a.internal_id}}</span>
              <span class="${{a.severity === 'CRITICA' ? 'badge-critical' : 'badge-high'}}">${{a.severity}}</span>
            </div>
            <div class="font-semibold text-slate-800 dark:text-slate-200 text-xs">${{a.class}}</div>
            <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 dark:text-slate-400">
              <span class="inline-flex items-center gap-1"><i data-lucide="user" class="w-3 h-3"></i> ${{a.user || 'N/A'}}</span>
              <span class="inline-flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3"></i> ${{a.site || 'Palma'}}</span>
              <span class="inline-flex items-center gap-1 font-mono"><i data-lucide="clock" class="w-3 h-3"></i> ${{a.timestamp.substring(0, 16)}}</span>
            </div>
            <details class="text-[11px] text-slate-500 dark:text-slate-400 pt-1.5 border-t border-slate-100 dark:border-slate-800">
              <summary class="cursor-pointer text-[#0784B7] dark:text-[#38BDF8] font-medium hover:underline">Ver detalles técnicos</summary>
              <div class="mt-1.5 p-2 rounded bg-slate-50 dark:bg-slate-800/80 font-mono text-[10px] break-all text-slate-700 dark:text-slate-300">
                ${{a.desc || a.category}}
              </div>
            </details>
          </div>
        `).join('');
      }}

      const tbSoar = document.getElementById('tbl-soar-actions');
      if (tbSoar) {{
        tbSoar.innerHTML = (SOAR_DATA || []).slice(0, 50).map(s => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40">
            <td class="font-mono text-slate-500 font-medium whitespace-nowrap">#${{s.id}}</td>
            <td class="font-medium text-slate-900 dark:text-white whitespace-nowrap">${{s.action}}</td>
            <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] whitespace-nowrap">${{s.target}}</td>
            <td class="text-slate-500">${{s.trigger}}</td>
            <td><span class="badge-low">${{s.status}}</span></td>
            <td class="text-slate-500 dark:text-slate-400 truncate max-w-sm">${{s.reason}}</td>
          </tr>
        `).join('');
      }}

      const cSoar = document.getElementById('cards-soar');
      if (cSoar) {{
        cSoar.innerHTML = (SOAR_DATA || []).slice(0, 50).map(s => `
          <div class="mobile-card space-y-1.5 text-xs">
            <div class="flex items-center justify-between gap-2">
              <span class="font-mono text-slate-500 font-bold">Orden #${{s.id}}</span>
              <span class="badge-low">${{s.status}}</span>
            </div>
            <div class="font-semibold text-slate-900 dark:text-white flex flex-wrap items-center gap-1.5">
              <span>${{s.action}}</span>
              <span class="font-mono text-[#0784B7] dark:text-[#38BDF8]">${{s.target}}</span>
            </div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">
              <span class="font-medium text-slate-700 dark:text-slate-300">Disparador:</span> ${{s.trigger}}
            </div>
            <p class="text-[11px] text-slate-600 dark:text-slate-300 break-words mt-1">${{s.reason}}</p>
          </div>
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
      const cards = document.querySelectorAll('#cards-alerts > div');
      cards.forEach(c => {{
        c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none';
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
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("index.html generado exitosamente con el nuevo diseño centrado en INCIDENTES!")

if __name__ == '__main__':
    main()
