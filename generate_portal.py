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
    crit_alerts = sum(1 for a in data.get('alerts', []) if a.get('severity') == 'CRITICA')
    high_alerts = sum(1 for a in data.get('alerts', []) if a.get('severity') == 'ALTA')
    med_alerts = sum(1 for a in data.get('alerts', []) if a.get('severity') == 'MEDIA')
    low_alerts = sum(1 for a in data.get('alerts', []) if a.get('severity') == 'BAJA')
    med_low_alerts = med_alerts + low_alerts
    crit_pct = round((crit_alerts / total_alerts) * 100, 1) if total_alerts else 0
    high_pct = round((high_alerts / total_alerts) * 100, 1) if total_alerts else 0
    med_pct = round((med_alerts / total_alerts) * 100, 1) if total_alerts else 0
    low_pct = round((low_alerts / total_alerts) * 100, 1) if total_alerts else 0

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
       PANTALLA DE INICIO DE SESIÓN CORPORATIVA SAMPOL (REAL DASHBOARD LOGIN)
       ========================================================================= -->
  <div id="sampol-auth-overlay" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/95 dark:bg-[#070B10] backdrop-blur-md p-4 transition-all duration-300">
    <div class="bg-white dark:bg-[#111A24] border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-sm w-full p-7 space-y-4">
      
      <!-- LOGO Y TÍTULO LIMPIO -->
      <div class="text-center">
        <div class="flex items-center justify-center gap-2 mb-3">
          <img src="./assets/brand/sampol_logo_color.png" alt="SAMPOL" class="h-7 w-auto block dark:hidden">
          <img src="./assets/brand/sampol_logo_blanco.png" alt="SAMPOL" class="h-7 w-auto hidden dark:block">
          <div class="h-4 w-px bg-slate-300 dark:bg-slate-700 mx-1"></div>
          <span class="text-xs font-bold text-slate-800 dark:text-slate-200 tracking-wider">NEXUS SOC</span>
        </div>
        <h2 class="text-lg font-bold text-slate-900 dark:text-white">Iniciar sesión</h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Introduce tus credenciales corporativas @sampol.com</p>
      </div>

      <!-- ALERTA DE ERROR SI EL DOMINIO NO ES @SAMPOL.COM -->
      <div id="auth-error-alert" class="hidden p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-400 text-center font-medium">
        Acceso restringido: Solo se permiten cuentas corporativas @sampol.com
      </div>

      <!-- FORMULARIO REAL DE LOGIN -->
      <form id="sampol-login-form" onsubmit="handleSampolLogin(event)" class="space-y-3.5">
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Correo corporativo
          </label>
          <input type="email" id="auth-email" required placeholder="usuario@sampol.com" value="analista.soc@sampol.com"
                 class="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0784B7] focus:border-transparent transition">
        </div>

        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="text-xs font-medium text-slate-700 dark:text-slate-300">Contraseña</label>
            <a href="javascript:void(0)" onclick="alert('Contacte con soporte IT de SAMPOL (dirti@sampol.com) para restablecer credenciales.');" class="text-[11px] text-[#0784B7] dark:text-[#38BDF8] hover:underline">¿Olvidaste tu contraseña?</a>
          </div>
          <input type="password" id="auth-password" required placeholder="••••••••••••" value="SampolSecure2026!"
                 class="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0784B7] focus:border-transparent transition">
        </div>

        <div class="flex items-center">
          <input type="checkbox" id="remember-me" checked class="w-3.5 h-3.5 rounded border-slate-300 text-[#0784B7] focus:ring-[#0784B7]">
          <label for="remember-me" class="ml-2 text-xs text-slate-600 dark:text-slate-400">Recordar este equipo</label>
        </div>

        <button type="submit" class="w-full py-2.5 px-4 rounded-lg bg-[#0784B7] hover:bg-[#066d97] text-white font-semibold text-xs shadow-sm hover:shadow transition flex items-center justify-center gap-2">
          <span>Iniciar sesión</span>
        </button>
      </form>

      <!-- SEPARADOR -->
      <div class="relative my-2">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-200 dark:border-slate-800"></div></div>
        <div class="relative flex justify-center text-[10px]"><span class="px-2 bg-white dark:bg-[#111A24] text-slate-400">o continuar con</span></div>
      </div>

      <!-- BOTÓN SSO MICROSOFT 365 REAL -->
      <button type="button" onclick="loginWithM365()" class="w-full py-2 px-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-medium transition flex items-center justify-center gap-2.5">
        <svg class="w-4 h-4 shrink-0" viewBox="0 0 21 21">
          <path fill="#f25022" d="M1 1h9v9H1z"/>
          <path fill="#00a4ef" d="M1 11h9v9H1z"/>
          <path fill="#7fba00" d="M11 1h9v9h-9z"/>
          <path fill="#ffb900" d="M11 11h9v9h-9z"/>
        </svg>
        <span>Microsoft 365 (SAMPOL SSO)</span>
      </button>

      <!-- FOOTER DISCRETO -->
      <div class="pt-2 text-center text-[10px] text-slate-400">
        <span>© 2026 Grupo SAMPOL · Uso exclusivo para personal autorizado</span>
      </div>

    </div>
  </div>

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

    <!-- NAVEGACIÓN OPERATIVA DEL SOC DASHBOARD -->
    <div class="flex-1 overflow-y-auto px-3 py-3 space-y-1.5 text-xs">
      <div class="px-2 mb-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Centro de Operaciones</div>

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

      <button onclick="switchTab('tab-soar')" id="btn-tab-soar" class="sidebar-nav-item w-full text-left">
        <i data-lucide="shield-check" class="w-4 h-4"></i>
        <span class="flex-1">Respuesta SOAR</span>
        <span class="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">{soar_count}</span>
      </button>
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

        <!-- PERFIL CONECTADO SAMPOL -->
        <div id="header-user-profile" class="flex items-center space-x-2 pl-2 border-l border-slate-200 dark:border-slate-700">
          <div id="header-avatar" class="w-7 h-7 rounded-full bg-[#0784B7] text-white flex items-center justify-center font-bold text-[11px]">
            AS
          </div>
          <div class="hidden sm:flex flex-col text-left">
            <span id="header-user-name" class="font-semibold text-slate-800 dark:text-slate-200 text-xs leading-tight">Analista SOC</span>
            <span id="header-user-email" class="text-[9.5px] text-[#0784B7] dark:text-[#38BDF8] leading-tight">analista.soc@sampol.com</span>
          </div>
          <button onclick="logoutSampol()" class="p-1 rounded text-slate-400 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition" title="Cerrar sesión corporativa (Demostrar Login)" aria-label="Cerrar sesión">
            <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
          </button>
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
      <section id="tab-resumen" class="tab-content min-w-0 w-full space-y-6">

        <!-- CABECERA DE OPERACIONES -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Centro de Operaciones SOC</h1>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-semibold border border-emerald-300 dark:border-emerald-800">En Vivo</span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Triaje pericial de alertas, monitorización de incidentes y respuesta SOAR en tiempo real.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-[11px] px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              93 Alertas Ingeridas
            </span>
            <button onclick="location.reload()" class="btn-sampol-secondary text-xs" title="Actualizar datos">
              <i data-lucide="rotate-cw" class="w-3.5 h-3.5"></i>
              <span class="hidden sm:inline">Actualizar</span>
            </button>
          </div>
        </div>

        <!-- 1. VALORES PRINCIPALES (TOP KPIS) -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">

          <div onclick="filterDashboardBySeverity('all')" class="sampol-card p-3.5 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Total Alertas</span>
              <i data-lucide="shield" class="w-4 h-4 text-[#0784B7] opacity-80"></i>
            </div>
            <div class="text-2xl font-bold text-slate-900 dark:text-white mt-1">{total_alerts}</div>
            <div class="text-[10px] text-slate-400 mt-0.5 font-medium">100% Taxonomía INCIBE</div>
          </div>

          <div onclick="filterDashboardBySeverity('CRITICA')" class="sampol-card p-3.5 cursor-pointer hover:border-rose-500 transition border-l-4 border-l-[#DC2626] bg-rose-50/25 dark:bg-rose-950/15">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-rose-600 dark:text-rose-400">Críticas (P1)</span>
              <span class="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span>
            </div>
            <div class="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1">{crit_alerts}</div>
            <div class="text-[10px] text-rose-500 mt-0.5 font-medium">SLA Inmediato &lt; 15m</div>
          </div>

          <div onclick="filterDashboardBySeverity('ALTA')" class="sampol-card p-3.5 cursor-pointer hover:border-orange-500 transition border-l-4 border-l-[#EA580C] bg-orange-50/25 dark:bg-orange-950/15">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-orange-600 dark:text-orange-400">Altas (P2)</span>
              <i data-lucide="alert-triangle" class="w-4 h-4 text-orange-500"></i>
            </div>
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400 mt-1">{high_alerts}</div>
            <div class="text-[10px] text-orange-500 mt-0.5 font-medium">SLA Prioritario &lt; 1h</div>
          </div>

          <div onclick="filterDashboardBySeverity('MEDIA')" class="sampol-card p-3.5 cursor-pointer hover:border-amber-500 transition border-l-4 border-l-[#D97706] bg-amber-50/20 dark:bg-amber-950/15">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-amber-600 dark:text-amber-400">Medias / Bajas</span>
              <i data-lucide="info" class="w-4 h-4 text-amber-500"></i>
            </div>
            <div class="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{med_low_alerts}</div>
            <div class="text-[10px] text-slate-400 mt-0.5 font-medium">{med_alerts} Medias · {low_alerts} Bajas</div>
          </div>

          <div onclick="switchTab('tab-soar')" class="sampol-card p-3.5 cursor-pointer hover:border-emerald-500 transition border-l-4 border-l-[#16A34A] bg-emerald-50/20 dark:bg-emerald-950/15">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">Contención SOAR</span>
              <i data-lucide="shield-check" class="w-4 h-4 text-emerald-500"></i>
            </div>
            <div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{soar_count}</div>
            <div class="text-[10px] text-slate-400 mt-0.5 font-medium">Aislamientos ejecutados</div>
          </div>

          <div onclick="switchTab('tab-soar')" class="sampol-card p-3.5 cursor-pointer hover:border-[#0784B7] transition border-l-4 border-l-[#0784B7]">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-[#0784B7] dark:text-[#38BDF8]">Reducción Ruido</span>
              <i data-lucide="sparkles" class="w-4 h-4 text-[#0784B7]"></i>
            </div>
            <div class="text-2xl font-bold text-slate-900 dark:text-white mt-1">65%</div>
            <div class="text-[10px] text-slate-400 mt-0.5 font-medium">Consolidación heurística</div>
          </div>

        </div>

        <!-- 2. GRÁFICO DE CANTIDAD DE ALERTAS SEGÚN LA GRAVEDAD -->
        <div class="sampol-card p-4 sm:p-5 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <div class="flex items-center gap-2">
                <i data-lucide="bar-chart-3" class="w-5 h-5 text-[#0784B7] dark:text-[#38BDF8]"></i>
                <h2 class="text-base font-bold text-slate-900 dark:text-white">Distribución de Alertas según Gravedad</h2>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Volumen cuantitativo de alertas catalogadas por criticidad e impacto operacional ({total_alerts} en total).</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400 font-mono">Taxonomía INCIBE v2.0</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
            <!-- CANVAS GRÁFICO DE BARRAS -->
            <div class="lg:col-span-7 min-w-0">
              <div class="h-64 sm:h-72 w-full min-w-0">
                <canvas id="chart-dashboard-severity"></canvas>
              </div>
            </div>

            <!-- TARJETAS INTERACTIVAS DE GRAVEDAD CON FILTRADO RÁPIDO -->
            <div class="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2.5">
              
              <div onclick="filterDashboardBySeverity('CRITICA')" class="p-3 rounded-lg border border-rose-200 dark:border-rose-900/60 bg-rose-50/40 dark:bg-rose-950/20 hover:border-rose-500 hover:shadow-sm cursor-pointer transition space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#DC2626]"></span>
                    <span class="font-bold text-xs text-rose-700 dark:text-rose-400">Crítica (P1)</span>
                  </div>
                  <span class="font-mono text-xs font-bold text-rose-700 dark:text-rose-400">{crit_alerts} ({crit_pct}%)</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div class="bg-[#DC2626] h-full" style="width: {crit_pct}%"></div>
                </div>
                <div class="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-300">
                  <span>Precursor Ransomware, C2, Exfiltración</span>
                  <span class="text-[10px] text-rose-600 font-semibold hover:underline">Filtrar →</span>
                </div>
              </div>

              <div onclick="filterDashboardBySeverity('ALTA')" class="p-3 rounded-lg border border-orange-200 dark:border-orange-900/60 bg-orange-50/40 dark:bg-orange-950/20 hover:border-orange-500 hover:shadow-sm cursor-pointer transition space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#EA580C]"></span>
                    <span class="font-bold text-xs text-orange-700 dark:text-orange-400">Alta (P2)</span>
                  </div>
                  <span class="font-mono text-xs font-bold text-orange-700 dark:text-orange-400">{high_alerts} ({high_pct}%)</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div class="bg-[#EA580C] h-full" style="width: {high_pct}%"></div>
                </div>
                <div class="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-300">
                  <span>Password Spray, Mov. Lateral, Privilegios</span>
                  <span class="text-[10px] text-orange-600 font-semibold hover:underline">Filtrar →</span>
                </div>
              </div>

              <div onclick="filterDashboardBySeverity('MEDIA')" class="p-3 rounded-lg border border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 hover:border-amber-500 hover:shadow-sm cursor-pointer transition space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#D97706]"></span>
                    <span class="font-bold text-xs text-amber-700 dark:text-amber-400">Media (P3)</span>
                  </div>
                  <span class="font-mono text-xs font-bold text-amber-700 dark:text-amber-400">{med_alerts} ({med_pct}%)</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div class="bg-[#D97706] h-full" style="width: {med_pct}%"></div>
                </div>
                <div class="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-300">
                  <span>Phishing genérico, escaneos externos</span>
                  <span class="text-[10px] text-amber-600 font-semibold hover:underline">Filtrar →</span>
                </div>
              </div>

              <div onclick="filterDashboardBySeverity('BAJA')" class="p-3 rounded-lg border border-emerald-200 dark:border-emerald-900/60 bg-emerald-50/40 dark:bg-emerald-950/20 hover:border-emerald-500 hover:shadow-sm cursor-pointer transition space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#16A34A]"></span>
                    <span class="font-bold text-xs text-emerald-700 dark:text-emerald-400">Baja (P4)</span>
                  </div>
                  <span class="font-mono text-xs font-bold text-emerald-700 dark:text-emerald-400">{low_alerts} ({low_pct}%)</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div class="bg-[#16A34A] h-full" style="width: {low_pct}%"></div>
                </div>
                <div class="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-300">
                  <span>Trazas rutinarias, telemetría informativa</span>
                  <span class="text-[10px] text-emerald-600 font-semibold hover:underline">Filtrar →</span>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- 3. PANEL DE GESTIÓN Y TRIAJE DE ALERTAS -->
        <div class="sampol-card p-4 sm:p-5 space-y-4">
          <!-- CABECERA Y BUSCADOR -->
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <div class="flex items-center gap-2">
                <i data-lucide="sliders-horizontal" class="w-5 h-5 text-[#0784B7] dark:text-[#38BDF8]"></i>
                <h2 class="text-base font-bold text-slate-900 dark:text-white">Panel para Gestión y Triaje de Alertas</h2>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Gestione el triaje pericial, modifique estados y aplique contención SOAR en cada alerta.</p>
            </div>
            
            <div class="w-full sm:w-80 min-w-0">
              <div class="relative">
                <i data-lucide="search" class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
                <input type="text" id="dash-alert-search" oninput="filterDashboardAlertsTable()" placeholder="Buscar por código, usuario, host, IP..." class="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
              </div>
            </div>
          </div>

          <!-- BOTONES DE FILTRO RÁPIDO -->
          <div class="flex flex-wrap items-center justify-between gap-2.5">
            <div class="flex flex-wrap items-center gap-1.5 text-xs" id="dash-severity-filters">
              <button onclick="filterDashboardBySeverity('all')" id="dash-filter-all" class="px-3 py-1 rounded-md text-xs font-semibold bg-[#0784B7] text-white">Todas ({total_alerts})</button>
              <button onclick="filterDashboardBySeverity('CRITICA')" id="dash-filter-CRITICA" class="px-3 py-1 rounded-md text-xs font-medium bg-white dark:bg-slate-800 text-rose-600 border border-slate-200 dark:border-slate-700 hover:bg-rose-50 dark:hover:bg-rose-950/30">Críticas ({crit_alerts})</button>
              <button onclick="filterDashboardBySeverity('ALTA')" id="dash-filter-ALTA" class="px-3 py-1 rounded-md text-xs font-medium bg-white dark:bg-slate-800 text-orange-600 border border-slate-200 dark:border-slate-700 hover:bg-orange-50 dark:hover:bg-orange-950/30">Altas ({high_alerts})</button>
              <button onclick="filterDashboardBySeverity('MEDIA')" id="dash-filter-MEDIA" class="px-3 py-1 rounded-md text-xs font-medium bg-white dark:bg-slate-800 text-amber-600 border border-slate-200 dark:border-slate-700 hover:bg-amber-50 dark:hover:bg-amber-950/30">Medias ({med_alerts})</button>
              <button onclick="filterDashboardBySeverity('BAJA')" id="dash-filter-BAJA" class="px-3 py-1 rounded-md text-xs font-medium bg-white dark:bg-slate-800 text-emerald-600 border border-slate-200 dark:border-slate-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/30">Bajas ({low_alerts})</button>
            </div>

            <div class="text-xs">
              <span id="dash-filtered-count" class="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Mostrando {total_alerts} de {total_alerts}</span>
            </div>
          </div>

          <!-- TABLA INTERACTIVA DE GESTIÓN -->
          <div class="hidden md:block overflow-x-auto max-h-[620px] min-w-0 w-full rounded-lg border border-slate-200 dark:border-slate-800">
            <table class="sampol-table min-w-full">
              <thead class="sticky top-0 z-10 bg-slate-50 dark:bg-slate-900 shadow-sm">
                <tr>
                  <th class="py-2.5 px-3">Código</th>
                  <th class="py-2.5 px-3">Fecha (UTC)</th>
                  <th class="py-2.5 px-3">Gravedad</th>
                  <th class="py-2.5 px-3">Clase INCIBE</th>
                  <th class="py-2.5 px-3">Activo / Usuario / IP</th>
                  <th class="py-2.5 px-3">Estado</th>
                  <th class="py-2.5 px-3 text-right">Gestión</th>
                </tr>
              </thead>
              <tbody id="tbl-dashboard-alerts" class="divide-y divide-slate-100 dark:divide-slate-800">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>

          <!-- TARJETAS ADAPTATIVAS (MÓVIL) -->
          <div id="cards-dashboard-alerts" class="block md:hidden space-y-2.5 max-h-[550px] overflow-y-auto min-w-0">
            <!-- Inyección JS -->
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
            Throughput operativo: 200.000 alertas/día (2,31 alertas/s sostenidas)
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

    </main>

  </div>

  <!-- =========================================================================
       MODAL DE DETALLE Y GESTIÓN DE INCIDENTE
       ========================================================================= -->
    <!-- =========================================================================
       MODAL DE GESTIÓN Y CONTENCIÓN DE ALERTA
       ========================================================================= -->
  <div id="alert-manage-modal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden flex items-center justify-center p-3 sm:p-4">
    <div class="bg-white dark:bg-[#111A24] border border-[#E2E8F0] dark:border-[#1E293B] rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-4 p-5 min-w-0">
      
      <!-- CABECERA MODAL -->
      <div class="flex items-start justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div>
          <div class="flex items-center gap-2">
            <span id="modal-manage-id" class="font-mono text-sm font-bold text-[#0784B7] dark:text-[#38BDF8]">SOC-20261103-...</span>
            <span id="modal-manage-sev" class="badge-critical">CRITICA</span>
            <span class="text-[11px] text-slate-400 font-mono" id="modal-manage-timestamp">2026-11-03 18:05</span>
          </div>
          <h2 class="text-base font-bold text-slate-900 dark:text-white mt-1">Gestión Pericial y Triaje de Alerta</h2>
        </div>
        <button onclick="closeAlertManageModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white p-1">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- METADATOS TÉCNICOS -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Clase INCIBE</div>
          <div id="modal-manage-class" class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Subclase INCIBE</div>
          <div id="modal-manage-subclass" class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Usuario / Cuenta</div>
          <div id="modal-manage-user" class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Host / Equipo</div>
          <div id="modal-manage-host" class="font-semibold text-[#0784B7] dark:text-[#38BDF8] mt-0.5 truncate">-</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2.5 text-xs">
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Dirección IP</div>
          <div id="modal-manage-ip" class="font-mono text-slate-700 dark:text-slate-300 mt-0.5 truncate">-</div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60">
          <div class="text-[10px] text-slate-400 font-medium">Sede / Ubicación</div>
          <div id="modal-manage-site" class="font-semibold text-slate-700 dark:text-slate-300 mt-0.5 truncate">-</div>
        </div>
      </div>

      <!-- DESCRIPCIÓN FORENSE DEL SENSOR -->
      <div class="space-y-1 text-xs">
        <strong class="text-slate-700 dark:text-slate-300 font-semibold">Telemetría y Evidencia Capturada</strong>
        <p id="modal-manage-desc" class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 font-mono text-[11px] leading-relaxed break-words"></p>
      </div>

      <!-- ACCIÓN DE RESPUESTA SOAR INMEDIATA -->
      <div class="p-3.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/60 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-800 dark:text-emerald-300">
            <i data-lucide="shield-check" class="w-4 h-4 text-emerald-600"></i>
            <span>Protocolo de Contención SOAR (Mitigación Automática)</span>
          </div>
          <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">Directriz 1 Activa</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Ejecuta regla de aislamiento en Firewall perimetral, corte de interfaz de red en EDR y revocación de tokens OAuth para el objetivo afectado.
        </p>
        <button id="btn-modal-soar-contain" onclick="executeAlertSoarAction()" class="btn-sampol-primary text-xs bg-emerald-600 hover:bg-emerald-700 text-white w-full sm:w-auto">
          <i data-lucide="shield-check" class="w-4 h-4"></i>
          <span>Ejecutar Contención SOAR (Aislar / Bloquear)</span>
        </button>
      </div>

      <!-- ACTUALIZACIÓN DE ESTADO OPERATIVO -->
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div>
          <span class="font-semibold text-slate-700 dark:text-slate-300">Estado de la Alerta:</span>
          <span class="text-slate-400 text-[11px] ml-1">Actualice la fase de triaje</span>
        </div>
        <div class="flex items-center gap-2">
          <select id="modal-manage-status-select" class="px-2.5 py-1 text-xs rounded bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200">
            <option value="Pendiente">Pendiente de Revisión</option>
            <option value="En Investigación">En Investigación</option>
            <option value="Contenida SOAR">Contenida SOAR</option>
            <option value="Falso Positivo">Falso Positivo</option>
            <option value="Cerrada">Cerrada</option>
          </select>
          <button onclick="saveAlertStatusChange()" class="btn-sampol-secondary text-xs py-1 px-3">Guardar</button>
        </div>
      </div>

      <!-- BOTONES DE PIE -->
      <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2 text-xs">
        <button onclick="closeAlertManageModal()" class="btn-sampol-secondary text-xs">
          Cerrar
        </button>
      </div>

    </div>
  </div>

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

      <!-- EXPLICACIÓN ESTRUCTURADA: ¿POR QUÉ REQUIERE ATENCIÓN ESTE INCIDENTE? -->
      <div class="p-3.5 rounded-lg bg-rose-50/80 dark:bg-rose-950/25 border border-rose-200 dark:border-rose-900/60 space-y-1.5">
        <div class="flex items-center gap-1.5 text-xs font-bold text-rose-700 dark:text-rose-400">
          <i data-lucide="shield-alert" class="w-4 h-4 text-rose-600"></i>
          <span>¿Por qué requiere atención este incidente?</span>
        </div>
        <p id="modal-inc-why" class="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed font-sans"></p>
      </div>

      <!-- DESCRIPCIÓN TÉCNICA Y RESUMEN -->
      <div class="space-y-1 text-xs">
        <strong class="text-slate-700 dark:text-slate-300 font-semibold">Resumen de Alerta y Evidencia de Origen</strong>
        <p id="modal-inc-desc" class="p-3 rounded bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 font-mono text-[11px] leading-relaxed break-words"></p>
      </div>

      <!-- EVIDENCIAS AGRUPADAS POR CATEGORÍA -->
      <div class="space-y-2 text-xs">
        <strong class="text-slate-700 dark:text-slate-300 font-semibold">Evidencias Correlacionadas por Categoría</strong>
        <div id="modal-inc-categories-container" class="space-y-2 pt-1"></div>
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
      'tab-soar': 'Respuesta SOAR'
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

      // 1. Explicación estructurada: ¿Por qué requiere atención?
      const whyEl = document.getElementById('modal-inc-why');
      if (whyEl) {{
        const topReasons = (inc.reasons || []).slice(0, 2).join(' y ');
        const assetTarget = inc.affected_asset && inc.affected_asset !== 'No identificado' ? inc.affected_asset : 'infraestructura corporativa';
        const userTarget = inc.affected_user && inc.affected_user !== 'No identificado' ? 'la cuenta ' + inc.affected_user : 'vector de acceso';
        whyEl.innerHTML = 'Este incidente ha alcanzado prioridad <strong class="text-rose-600 dark:text-rose-400">' + inc.priority + '</strong> con un nivel de riesgo de <strong>' + (inc.risk_score || 85) + '/100</strong>. Las evidencias auditadas confirman <strong>' + (topReasons || 'amenaza técnica activa') + '</strong> sobre <strong>' + userTarget + '</strong> y el activo <strong>' + assetTarget + '</strong>. Requiere intervención inmediata del analista según el SLA operativo de 15 minutos.';
      }}

      // 2. Agrupación estructurada de evidencias en acordeones colapsables
      const catContainer = document.getElementById('modal-inc-categories-container');
      if (catContainer) {{
        const rawReasons = inc.reasons || [];
        const cats = {{
          'Malware y Precursores Ransomware': [],
          'Red y Canales de Comando & Control (C2)': [],
          'Autenticación e Intentos de Acceso': [],
          'Identidad, Privilegios y Persistencia': [],
          'Criticidad de Activos y Entorno Industrial': [],
          'Correlación y Volumen de Alertas': [],
          'Otras Evidencias de Seguridad': []
        }};

        rawReasons.forEach(r => {{
          const rLow = r.toLowerCase();
          if (rLow.includes('malware') || rLow.includes('modify') || rLow.includes('dañino') || rLow.includes('ransom')) {{
            cats['Malware y Precursores Ransomware'].push(r);
          }} else if (rLow.includes('c2') || rLow.includes('comando') || rLow.includes('tráfico') || rLow.includes('red')) {{
            cats['Red y Canales de Comando & Control (C2)'].push(r);
          }} else if (rLow.includes('credencial') || rLow.includes('spray') || rLow.includes('autentic') || rLow.includes('acceso')) {{
            cats['Autenticación e Intentos de Acceso'].push(r);
          }} else if (rLow.includes('privilegi') || rLow.includes('admin') || rLow.includes('apt') || rLow.includes('lateral')) {{
            cats['Identidad, Privilegios y Persistencia'].push(r);
          }} else if (rLow.includes('crítica') || rLow.includes('ot') || rLow.includes('planta') || rLow.includes('activo')) {{
            cats['Criticidad de Activos y Entorno Industrial'].push(r);
          }} else if (rLow.includes('volumen') || rLow.includes('masivo') || rLow.includes('correlacionad') || rLow.includes('reiterad')) {{
            cats['Correlación y Volumen de Alertas'].push(r);
          }} else {{
            cats['Otras Evidencias de Seguridad'].push(r);
          }}
        }});

        let catHtml = '';
        Object.entries(cats).forEach(([catTitle, items]) => {{
          if (items.length > 0) {{
            catHtml += '<details class="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50 p-2.5 space-y-1.5 transition" open>' +
              '<summary class="cursor-pointer text-xs font-semibold text-slate-800 dark:text-slate-200 flex items-center justify-between select-none">' +
                '<span class="flex items-center gap-2">' +
                  '<span class="w-2 h-2 rounded-full bg-[#0784B7]"></span>' +
                  '<span>' + catTitle + '</span>' +
                '</span>' +
                '<span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-200 dark:bg-slate-700 font-mono text-slate-600 dark:text-slate-300">' + items.length + '</span>' +
              '</summary>' +
              '<ul class="pt-2 pl-4 space-y-1 text-[11px] text-slate-600 dark:text-slate-300 list-disc">' +
                items.map(it => '<li>' + it + '</li>').join('') +
              '</ul>' +
            '</details>';
          }}
        }});

        catContainer.innerHTML = catHtml || '<div class="text-slate-400 text-[11px]">Sin factores adicionales registrados.</div>';
      }}
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
      renderDashboardAlertsTable();
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
      initSampolAuth();
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

      const chDashSev = document.getElementById('chart-dashboard-severity');
      if (chDashSev && typeof Chart !== 'undefined') {{
        new Chart(chDashSev, {{
          type: 'bar',
          data: {{
            labels: ['Crítica (P1)', 'Alta (P2)', 'Media (P3)', 'Baja (P4)'],
            datasets: [{{
              label: 'Cantidad de Alertas',
              data: [{crit_alerts}, {high_alerts}, {med_alerts}, {low_alerts}],
              backgroundColor: ['#DC2626', '#EA580C', '#D97706', '#16A34A'],
              borderRadius: 6,
              borderWidth: 0,
              barThickness: 42
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{ display: false }},
              tooltip: {{
                callbacks: {{
                  label: function(ctx) {{
                    const total = {total_alerts};
                    const pct = ((ctx.raw / total) * 100).toFixed(1);
                    return ' ' + ctx.raw + ' alertas (' + pct + '%)';
                  }}
                }}
              }}
            }},
            scales: {{
              x: {{
                grid: {{ display: false }},
                ticks: {{
                  font: {{ size: 11, weight: '600' }},
                  color: '#64748B'
                }}
              }},
              y: {{
                beginAtZero: true,
                grid: {{ color: 'rgba(226, 232, 240, 0.6)' }},
                ticks: {{
                  font: {{ size: 11 }},
                  color: '#64748B',
                  stepSize: 10
                }}
              }}
            }}
          }}
        }});
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

    let DASH_CURRENT_SEVERITY = 'all';
    let DASH_ALERT_STORE = (ALERTS_DATA || []).map(function(a, idx) {{
      return Object.assign({{}}, a, {{
        status: a.status || (a.severity === 'CRITICA' ? 'En Investigación' : 'Pendiente'),
        idx: idx
      }});
    }});

    function renderDashboardAlertsTable() {{
      const searchInput = document.getElementById('dash-alert-search');
      const q = (searchInput ? searchInput.value : '').toLowerCase();
      const tb = document.getElementById('tbl-dashboard-alerts');
      const cards = document.getElementById('cards-dashboard-alerts');
      const countEl = document.getElementById('dash-filtered-count');
      if (!tb) return;

      const filtered = DASH_ALERT_STORE.filter(function(a) {{
        const matchSev = DASH_CURRENT_SEVERITY === 'all' || a.severity === DASH_CURRENT_SEVERITY;
        const matchQ = !q || 
          (a.internal_id && a.internal_id.toLowerCase().indexOf(q) !== -1) ||
          (a.user && a.user.toLowerCase().indexOf(q) !== -1) ||
          (a.host && a.host.toLowerCase().indexOf(q) !== -1) ||
          (a.ip && a.ip.toLowerCase().indexOf(q) !== -1) ||
          (a.class && a.class.toLowerCase().indexOf(q) !== -1) ||
          (a.subclass && a.subclass.toLowerCase().indexOf(q) !== -1) ||
          (a.desc && a.desc.toLowerCase().indexOf(q) !== -1);
        return matchSev && matchQ;
      }});

      if (countEl) {{
        countEl.textContent = 'Mostrando ' + filtered.length + ' de ' + DASH_ALERT_STORE.length + ' alertas';
      }}

      if (filtered.length === 0) {{
        tb.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-400 text-xs">No se encontraron alertas para los filtros seleccionados.</td></tr>';
        if (cards) cards.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs">No se encontraron alertas.</div>';
        return;
      }}

      tb.innerHTML = filtered.map(function(a) {{
        const badgeClass = a.severity === 'CRITICA' ? 'badge-critical' : 
                           a.severity === 'ALTA' ? 'badge-high' : 
                           a.severity === 'MEDIA' ? 'badge-medium' : 'badge-low';
        
        let statusBadge = '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">Pendiente</span>';
        if (a.status === 'Contenida SOAR') {{
          statusBadge = '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"><i data-lucide="check" class="w-3 h-3"></i> Contenido</span>';
        }} else if (a.status === 'En Investigación') {{
          statusBadge = '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-800">En Investigación</span>';
        }}

        const entity = a.user && a.user !== 'No identificado' 
          ? a.user 
          : (a.host && a.host !== 'No identificado' 
          ? a.host 
          : (a.ip && a.ip !== 'N/A' ? a.ip : 'Sensor Global'));

        const ipSite = a.ip && a.ip !== 'N/A' ? 'IP: ' + a.ip : (a.site || 'Palma');
        const timestampStr = (a.timestamp || '').substring(0, 16);

        return '<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">' +
          '<td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-bold text-xs whitespace-nowrap">' + a.internal_id + '</td>' +
          '<td class="font-mono text-[11px] text-slate-400 whitespace-nowrap">' + timestampStr + '</td>' +
          '<td><span class="' + badgeClass + '">' + a.severity + '</span></td>' +
          '<td>' +
            '<div class="font-semibold text-slate-800 dark:text-slate-200 text-xs">' + a.class + '</div>' +
            '<div class="text-[10px] text-slate-400 truncate max-w-[180px]">' + (a.subclass || '') + '</div>' +
          '</td>' +
          '<td>' +
            '<div class="font-mono text-xs text-slate-700 dark:text-slate-300 truncate max-w-[170px]">' + entity + '</div>' +
            '<div class="text-[10px] text-slate-400 font-mono">' + ipSite + '</div>' +
          '</td>' +
          '<td>' + statusBadge + '</td>' +
          '<td class="text-right whitespace-nowrap">' +
            '<button data-id="' + a.internal_id + '" onclick="openAlertManageModal(this.dataset.id)" class="px-2.5 py-1 rounded bg-[#0784B7]/10 hover:bg-[#0784B7] text-[#0784B7] hover:text-white dark:bg-[#38BDF8]/10 dark:hover:bg-[#38BDF8] dark:text-[#38BDF8] dark:hover:text-slate-900 font-semibold text-xs transition inline-flex items-center gap-1.5">' +
              '<i data-lucide="sliders" class="w-3.5 h-3.5"></i>' +
              '<span>Gestionar</span>' +
            '</button>' +
          '</td>' +
        '</tr>';
      }}).join('');

      if (cards) {{
        cards.innerHTML = filtered.map(function(a) {{
          const badgeClass = a.severity === 'CRITICA' ? 'badge-critical' : 
                             a.severity === 'ALTA' ? 'badge-high' : 
                             a.severity === 'MEDIA' ? 'badge-medium' : 'badge-low';
          const entity = a.user || a.host || a.ip || 'N/A';
          const timestampStr = (a.timestamp || '').substring(0, 16);
          const desc = a.desc || a.category || '';
          const status = a.status || 'Pendiente';

          return '<div class="mobile-card space-y-2 p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 text-xs shadow-sm">' +
            '<div class="flex items-center justify-between">' +
              '<span class="font-mono font-bold text-xs text-[#0784B7] dark:text-[#38BDF8]">' + a.internal_id + '</span>' +
              '<span class="' + badgeClass + '">' + a.severity + '</span>' +
            '</div>' +
            '<div class="font-semibold text-slate-800 dark:text-slate-200">' + a.class + (a.subclass ? ' · ' + a.subclass : '') + '</div>' +
            '<div class="text-[11px] text-slate-500 dark:text-slate-400 flex flex-wrap gap-2">' +
              '<span><strong>Afectado:</strong> ' + entity + '</span>' +
              '<span><strong>Fecha:</strong> ' + timestampStr + '</span>' +
            '</div>' +
            '<p class="text-[11px] text-slate-600 dark:text-slate-300 line-clamp-2">' + desc + '</p>' +
            '<div class="pt-2 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between">' +
              '<span class="text-[10px] text-slate-400">' + status + '</span>' +
              '<button data-id="' + a.internal_id + '" onclick="openAlertManageModal(this.dataset.id)" class="px-2.5 py-1 rounded bg-[#0784B7] text-white font-medium text-xs flex items-center gap-1">' +
                '<i data-lucide="sliders" class="w-3.5 h-3.5"></i>' +
                '<span>Gestionar</span>' +
              '</button>' +
            '</div>' +
          '</div>';
        }}).join('');
      }}

      if (window.lucide) lucide.createIcons();
    }}

    function filterDashboardAlertsTable() {{
      renderDashboardAlertsTable();
    }}

    function filterDashboardBySeverity(sev) {{
      DASH_CURRENT_SEVERITY = sev;
      ['all', 'CRITICA', 'ALTA', 'MEDIA', 'BAJA'].forEach(function(s) {{
        const btn = document.getElementById('dash-filter-' + s);
        if (btn) {{
          if (s === sev) {{
            btn.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-[#0784B7] text-white shadow-sm';
          }} else {{
            const txtColor = s === 'CRITICA' ? 'text-rose-600' : s === 'ALTA' ? 'text-orange-600' : s === 'MEDIA' ? 'text-amber-600' : s === 'BAJA' ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300';
            btn.className = 'px-3 py-1 rounded-md text-xs font-medium bg-white dark:bg-slate-800 ' + txtColor + ' border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50';
          }}
        }}
      }});
      renderDashboardAlertsTable();
      const el = document.getElementById('dash-alert-search');
      if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}

    let CURRENT_MANAGE_ALERT = null;

    function openAlertManageModal(id) {{
      const alertObj = DASH_ALERT_STORE.find(function(a) {{ return a.internal_id === id; }});
      if (!alertObj) return;
      CURRENT_MANAGE_ALERT = alertObj;

      document.getElementById('modal-manage-id').textContent = alertObj.internal_id;
      const sevEl = document.getElementById('modal-manage-sev');
      sevEl.textContent = alertObj.severity;
      sevEl.className = alertObj.severity === 'CRITICA' ? 'badge-critical' : alertObj.severity === 'ALTA' ? 'badge-high' : alertObj.severity === 'MEDIA' ? 'badge-medium' : 'badge-low';
      
      document.getElementById('modal-manage-timestamp').textContent = (alertObj.timestamp || '').substring(0, 19);
      document.getElementById('modal-manage-class').textContent = alertObj.class;
      document.getElementById('modal-manage-subclass').textContent = alertObj.subclass || 'Sin subclase especificada';
      document.getElementById('modal-manage-user').textContent = alertObj.user && alertObj.user !== 'No identificado' ? alertObj.user : 'No especificado';
      document.getElementById('modal-manage-host').textContent = alertObj.host && alertObj.host !== 'No identificado' ? alertObj.host : 'No especificado';
      document.getElementById('modal-manage-ip').textContent = alertObj.ip && alertObj.ip !== 'N/A' ? alertObj.ip : 'Sin IP registrada';
      document.getElementById('modal-manage-site').textContent = alertObj.site || 'SAMPOL HQ (Palma)';
      document.getElementById('modal-manage-desc').textContent = alertObj.desc || alertObj.category || 'Sin descripción detallada.';
      document.getElementById('modal-manage-status-select').value = alertObj.status || 'Pendiente';

      const btnSoar = document.getElementById('btn-modal-soar-contain');
      if (alertObj.status === 'Contenida SOAR') {{
        btnSoar.disabled = true;
        btnSoar.className = 'btn-sampol-secondary text-xs opacity-50 cursor-not-allowed';
        btnSoar.innerHTML = '<i data-lucide="check-check" class="w-4 h-4"></i><span>Contención Ya Aplicada</span>';
      }} else {{
        btnSoar.disabled = false;
        btnSoar.className = 'btn-sampol-primary text-xs bg-emerald-600 hover:bg-emerald-700 text-white';
        btnSoar.innerHTML = '<i data-lucide="shield-check" class="w-4 h-4"></i><span>Ejecutar Contención SOAR (Aislar / Bloquear)</span>';
      }}

      document.getElementById('alert-manage-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }}

    function closeAlertManageModal() {{
      document.getElementById('alert-manage-modal').classList.add('hidden');
      CURRENT_MANAGE_ALERT = null;
    }}

    function executeAlertSoarAction() {{
      if (!CURRENT_MANAGE_ALERT) return;
      CURRENT_MANAGE_ALERT.status = 'Contenida SOAR';
      const target = CURRENT_MANAGE_ALERT.host || CURRENT_MANAGE_ALERT.user || CURRENT_MANAGE_ALERT.ip;
      showToastNotification('Acción SOAR ejecutada: Activo ' + target + ' aislado preventivamente.');
      renderDashboardAlertsTable();
      openAlertManageModal(CURRENT_MANAGE_ALERT.internal_id);
    }}

    function saveAlertStatusChange() {{
      if (!CURRENT_MANAGE_ALERT) return;
      const newStatus = document.getElementById('modal-manage-status-select').value;
      CURRENT_MANAGE_ALERT.status = newStatus;
      showToastNotification('Estado de alerta ' + CURRENT_MANAGE_ALERT.internal_id + ' actualizado a: ' + newStatus);
      renderDashboardAlertsTable();
      closeAlertManageModal();
    }}

    function showToastNotification(msg) {{
      let toast = document.getElementById('sampol-toast');
      if (!toast) {{
        toast = document.createElement('div');
        toast.id = 'sampol-toast';
        toast.className = 'fixed bottom-5 right-5 z-50 px-4 py-3 rounded-lg shadow-xl bg-slate-900 text-white text-xs flex items-center gap-2 border border-slate-700 transition-all duration-300';
        document.body.appendChild(toast);
      }}
      toast.innerHTML = '<i data-lucide="info" class="w-4 h-4 text-[#38BDF8]"></i><span>' + msg + '</span>';
      toast.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
      setTimeout(function() {{
        toast.classList.add('hidden');
      }}, 4000);
    }}

    function initSampolAuth() {{
      const savedUser = sessionStorage.getItem('sampol_user');
      const overlay = document.getElementById('sampol-auth-overlay');
      if (savedUser) {{
        try {{
          const user = JSON.parse(savedUser);
          applyUserSession(user);
          if (overlay) overlay.classList.add('hidden');
        }} catch(e) {{
          sessionStorage.removeItem('sampol_user');
          if (overlay) overlay.classList.remove('hidden');
        }}
      }} else {{
        if (overlay) overlay.classList.remove('hidden');
      }}
    }}

    function handleSampolLogin(e) {{
      if (e) e.preventDefault();
      const emailInput = document.getElementById('auth-email');
      const errorAlert = document.getElementById('auth-error-alert');
      const email = (emailInput ? emailInput.value : '').trim();

      if (!email.toLowerCase().endsWith('@sampol.com')) {{
        if (errorAlert) {{
          errorAlert.classList.remove('hidden');
          errorAlert.textContent = 'Acceso restringido: Solo se permiten cuentas corporativas @sampol.com';
        }}
        return;
      }}

      if (errorAlert) errorAlert.classList.add('hidden');

      let name = 'Carlos Gómez';
      let role = 'Analista SOC L2';
      if (email.toLowerCase().includes('dirti') || email.toLowerCase().includes('director')) {{
        name = 'Director de TI';
        role = 'Dirección de TI (C-Level)';
      }} else if (email.toLowerCase().includes('admin')) {{
        name = 'Administrador SOC';
        role = 'Administrador de Seguridad';
      }} else {{
        const parts = email.split('@')[0].split('.');
        if (parts.length >= 2) {{
          name = parts[0].charAt(0).toUpperCase() + parts[0].slice(1) + ' ' + parts[1].charAt(0).toUpperCase() + parts[1].slice(1);
        }} else {{
          name = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
        }}
      }}

      const user = {{ email, name, role }};
      sessionStorage.setItem('sampol_user', JSON.stringify(user));
      applyUserSession(user);

      const overlay = document.getElementById('sampol-auth-overlay');
      if (overlay) {{
        overlay.classList.add('opacity-0');
        setTimeout(() => {{
          overlay.classList.add('hidden');
          overlay.classList.remove('opacity-0');
        }}, 200);
      }}

      showToastNotification('Sesión iniciada correctamente como ' + user.name);
    }}

    function loginWithM365() {{
      const user = {{
        email: 'carlos.gomez@sampol.com',
        name: 'Carlos Gómez',
        role: 'Analista SOC L2 (M365)'
      }};
      sessionStorage.setItem('sampol_user', JSON.stringify(user));
      applyUserSession(user);

      const overlay = document.getElementById('sampol-auth-overlay');
      if (overlay) {{
        overlay.classList.add('opacity-0');
        setTimeout(() => {{
          overlay.classList.add('hidden');
          overlay.classList.remove('opacity-0');
        }}, 200);
      }}

      showToastNotification('Autenticado vía Microsoft 365 Entra ID (SAMPOL)');
    }}

    function applyUserSession(user) {{
      const avatar = document.getElementById('header-avatar');
      const nameEl = document.getElementById('header-user-name');
      const emailEl = document.getElementById('header-user-email');

      if (nameEl) nameEl.textContent = user.name || user.role;
      if (emailEl) emailEl.textContent = user.email;
      if (avatar) {{
        const parts = (user.name || user.email).split(' ');
        const initials = parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : user.email.slice(0, 2).toUpperCase();
        avatar.textContent = initials;
      }}
    }}

    function logoutSampol() {{
      sessionStorage.removeItem('sampol_user');
      const overlay = document.getElementById('sampol-auth-overlay');
      const errorAlert = document.getElementById('auth-error-alert');
      if (errorAlert) errorAlert.classList.add('hidden');
      if (overlay) overlay.classList.remove('hidden');
      showToastNotification('Sesión cerrada.');
    }}

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
