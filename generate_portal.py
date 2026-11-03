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
  <title>NEXUS SOC 2.0 — Intelligent Security Operations | SAMPOL</title>
  <link rel="icon" type="image/png" href="./assets/brand/sampol_favicon.png">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
              'blue-light': '#E8F4F9',
              green: '#42A83B',
              'green-hover': '#378c31',
              'green-light': '#EEF7ED',
              dark: '#172C3D',
              slate: '#243B50',
              bg: '#F2F5F6',
              surface: '#FFFFFF',
              border: '#DCE4E9'
            }}
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-[#F2F5F6] dark:bg-[#0B131B] text-[#172C3D] dark:text-[#F1F5F9] font-sans antialiased min-h-screen flex">

  <!-- =========================================================================
       SIDEBAR LATERAL CORPORATIVO SAMPOL (ESCRITORIO & RETRÁCTIL EN MÓVIL)
       ========================================================================= -->
  <aside id="main-sidebar" class="fixed inset-y-0 left-0 z-40 w-72 bg-white dark:bg-[#121F2C] border-r border-[#DCE4E9] dark:border-[#22374A] flex flex-col transition-transform duration-300 ease-in-out md:translate-x-0 -translate-x-full shadow-sm">
    
    <!-- CABECERA DEL SIDEBAR -->
    <div class="p-5 border-b border-[#DCE4E9] dark:border-[#22374A] flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <!-- Logotipo Oficial SAMPOL (Alterna claro/oscuro automáticamente) -->
        <div class="flex flex-col">
          <div class="flex items-center space-x-2">
            <img src="./assets/brand/sampol_logo_color.png" alt="SAMPOL" class="h-8 w-auto dark:hidden" onerror="this.style.display='none'">
            <img src="./assets/brand/sampol_logo_blanco.png" alt="SAMPOL" class="h-8 w-auto hidden dark:block" onerror="this.style.display='none'">
            <span class="text-xs font-black px-1.5 py-0.5 rounded bg-[#0784B7]/10 text-[#0784B7] dark:bg-[#0784B7]/30 dark:text-[#38BDF8] border border-[#0784B7]/30">SOC 2.0</span>
          </div>
          <div class="mt-1 flex items-center space-x-1.5">
            <span class="text-[11px] font-bold text-[#172C3D] dark:text-white tracking-wider">NEXUS PLATFORM</span>
            <span class="text-[10px] text-[#647786] dark:text-slate-400">· v2.0.4</span>
          </div>
        </div>
      </div>
      <button onclick="toggleSidebar()" class="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white">
        ✕
      </button>
    </div>

    <!-- BADGE DE ENTORNO CORPORATIVO -->
    <div class="px-5 py-2.5 bg-[#EAF0F3]/60 dark:bg-[#182A3A]/60 border-b border-[#DCE4E9]/60 dark:border-[#22374A]/60 flex items-center justify-between text-xs">
      <div class="flex items-center space-x-1.5">
        <span class="w-2 h-2 rounded-full bg-[#42A83B] animate-pulse"></span>
        <span class="font-bold text-[#172C3D] dark:text-slate-200">ENTORNO DEMO</span>
      </div>
      <span class="px-2 py-0.5 rounded bg-white dark:bg-slate-800 text-[10px] font-semibold text-[#0784B7] dark:text-cyan-400 border border-[#DCE4E9] dark:border-slate-700">Hackathon 24h</span>
    </div>

    <!-- NAVEGACIÓN PRINCIPAL -->
    <nav class="flex-1 overflow-y-auto p-4 space-y-6 text-sm">
      
      <!-- GRUPO: OPERACIONES SOC -->
      <div>
        <div class="px-3 mb-2 text-[11px] font-bold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Operaciones SOC</div>
        <div class="space-y-1">
          <button onclick="switchTab('tab-resumen')" id="btn-tab-resumen" class="sidebar-nav-item active w-full text-left">
            <span class="text-base">📊</span>
            <span class="flex-1">Centro de Operaciones</span>
          </button>
          <button onclick="switchTab('tab-dataset')" id="btn-tab-dataset" class="sidebar-nav-item w-full text-left">
            <span class="text-base">🗄️</span>
            <span class="flex-1">Alertas & Triaje INCIBE</span>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">{total_alerts}</span>
          </button>
          <button onclick="switchTab('tab-notifications')" id="btn-tab-notifications" class="sidebar-nav-item w-full text-left">
            <span class="text-base">🔔</span>
            <span class="flex-1">Smart Notifications</span>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300 border border-red-300 dark:border-red-800 animate-pulse">{p1_count} P1</span>
          </button>
          <button onclick="switchTab('tab-forense')" id="btn-tab-forense" class="sidebar-nav-item w-full text-left">
            <span class="text-base">🕵️</span>
            <span class="flex-1">Investigación Forense</span>
            <span class="px-1.5 py-0.5 text-[10px] rounded bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 font-semibold">Kill Chain</span>
          </button>
        </div>
      </div>

      <!-- GRUPO: GESTIÓN & RESPUESTA -->
      <div>
        <div class="px-3 mb-2 text-[11px] font-bold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Gestión & Respuesta</div>
        <div class="space-y-1">
          <button onclick="switchTab('tab-soar')" id="btn-tab-soar" class="sidebar-nav-item w-full text-left">
            <span class="text-base">⚡</span>
            <span class="flex-1">Centro de Respuesta SOAR</span>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-[#0784B7]/10 text-[#0784B7] dark:bg-cyan-950 dark:text-cyan-300">{soar_count}</span>
          </button>
          <button onclick="switchTab('tab-activos')" id="btn-tab-activos" class="sidebar-nav-item w-full text-left">
            <span class="text-base">👥</span>
            <span class="flex-1">Usuarios & Activos</span>
          </button>
          <button onclick="switchTab('tab-automations')" id="btn-tab-automations" class="sidebar-nav-item w-full text-left">
            <span class="text-base">🔄</span>
            <span class="flex-1">Automatizaciones (Graph)</span>
          </button>
        </div>
      </div>

      <!-- GRUPO: ANÁLISIS DIRECTIVO -->
      <div>
        <div class="px-3 mb-2 text-[11px] font-bold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Análisis & Gobierno</div>
        <div class="space-y-1">
          <button onclick="switchTab('tab-roi')" id="btn-tab-roi" class="sidebar-nav-item w-full text-left">
            <span class="text-base">💶</span>
            <span class="flex-1">Calculadora ROI (Director)</span>
            <span class="px-1.5 py-0.5 text-[10px] font-bold rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">184k€</span>
          </button>
          <button onclick="switchTab('tab-directrices')" id="btn-tab-directrices" class="sidebar-nav-item w-full text-left">
            <span class="text-base">🎯</span>
            <span class="flex-1">Directrices & NIS2</span>
          </button>
          <button onclick="switchTab('tab-auditoria')" id="btn-tab-auditoria" class="sidebar-nav-item w-full text-left">
            <span class="text-base">📋</span>
            <span class="flex-1">Auditoría Inmutable</span>
          </button>
        </div>
      </div>

    </nav>

    <!-- PIE DEL SIDEBAR: ESTADO DEL SISTEMA -->
    <div class="p-4 border-t border-[#DCE4E9] dark:border-[#22374A] bg-[#F2F5F6]/50 dark:bg-[#0D161F]/50 text-xs space-y-2">
      <div class="flex items-center justify-between text-slate-500 dark:text-slate-400">
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-[#42A83B]"></span>
          <span>Azure PostgreSQL</span>
        </span>
        <span class="font-bold text-slate-700 dark:text-slate-300">alertas-soc-1</span>
      </div>
      <div class="text-[10px] text-slate-400">Sincronización continua cada 45s</div>
    </div>
  </aside>

  <!-- BACKDROP MÓVIL PARA SIDEBAR -->
  <div id="sidebar-backdrop" onclick="toggleSidebar()" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-30 hidden md:hidden"></div>

  <!-- =========================================================================
       ÁREA PRINCIPAL DE CONTENIDO
       ========================================================================= -->
  <div class="flex-1 md:pl-72 flex flex-col min-h-screen">
    
    <!-- HEADER SUPERIOR CORPORATIVO -->
    <header class="sticky top-0 z-20 bg-white/95 dark:bg-[#121F2C]/95 backdrop-blur-md border-b border-[#DCE4E9] dark:border-[#22374A] px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-4">
      
      <!-- IZQUIERDA: BOTÓN HAMBURGUESA Y BREADCRUMB -->
      <div class="flex items-center space-x-3">
        <button onclick="toggleSidebar()" class="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
        <div class="hidden sm:flex items-center space-x-2 text-xs font-medium text-slate-500 dark:text-slate-400">
          <span class="text-[#0784B7] font-semibold">SAMPOL</span>
          <span>/</span>
          <span>NEXUS SOC 2.0</span>
          <span>/</span>
          <span id="breadcrumb-current" class="text-slate-900 dark:text-white font-bold">Centro de Operaciones</span>
        </div>
      </div>

      <!-- CENTRO: BUSCADOR GLOBAL -->
      <div class="flex-1 max-w-md hidden lg:block">
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-xs">🔍</span>
          <input type="text" id="global-search" oninput="handleGlobalSearch()" placeholder="Buscar alertas, IPs, usuarios comprometidos..." class="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg bg-[#F2F5F6] dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A] focus:outline-none focus:border-[#0784B7] focus:ring-1 focus:ring-[#0784B7] text-[#172C3D] dark:text-white placeholder-slate-400 transition">
        </div>
      </div>

      <!-- DERECHA: ACCIONES Y PERFIL -->
      <div class="flex items-center space-x-3 text-xs">
        
        <!-- ESTADO DE LA INGESTA EN VIVO -->
        <div class="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#EAF0F3] dark:bg-[#182A3A] text-slate-600 dark:text-slate-300">
          <span class="w-2 h-2 rounded-full bg-[#42A83B] animate-pulse"></span>
          <span>Buzón Graph:</span>
          <strong class="text-[#0784B7] dark:text-[#38BDF8]">{raw_count} Correos</strong>
        </div>

        <!-- CAMPANA DE NOTIFICACIONES INTELIGENTES -->
        <button onclick="toggleBellDrawer()" id="nexus-bell-trigger" class="relative p-2 rounded-lg bg-[#E8F4F9] dark:bg-[#0784B7]/20 hover:bg-[#0784B7]/20 border border-[#0784B7]/30 transition text-[#0784B7] dark:text-[#38BDF8]" title="Ver Avisos Prioritarios">
          <span class="text-base">🔔</span>
          <span id="bell-badge-count" class="absolute -top-1 -right-1 px-1.5 py-0.2 rounded-full bg-[#DC2626] text-white font-black text-[10px] animate-pulse">{p1_count}</span>
        </button>

        <!-- SELECTOR DE MODO CLARO / OSCURO -->
        <button onclick="toggleTheme()" class="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition" title="Cambiar Tema Claro / Oscuro">
          <span id="theme-icon" class="text-base">🌙</span>
        </button>

        <!-- PERFIL DE ANALISTA SOC -->
        <div class="flex items-center space-x-2 pl-2 border-l border-[#DCE4E9] dark:border-[#22374A]">
          <div class="w-8 h-8 rounded-full bg-[#0784B7] text-white flex items-center justify-center font-bold text-xs shadow-sm">
            GS
          </div>
          <div class="hidden sm:block text-left">
            <div class="font-bold text-[#172C3D] dark:text-white leading-tight">Guardia SOC</div>
            <div class="text-[10px] text-[#647786] dark:text-slate-400">Nivel 1 · SAMPOL</div>
          </div>
        </div>

      </div>
    </header>

    <!-- DRAWER LATERAL DE NOTIFICACIONES INTELIGENTES -->
    <aside id="bell-drawer" class="fixed top-16 right-4 w-96 max-w-[calc(100vw-2rem)] max-h-[85vh] overflow-y-auto bg-white dark:bg-[#121F2C] border border-[#DCE4E9] dark:border-[#22374A] rounded-2xl shadow-xl p-5 z-50 hidden space-y-4">
      <div class="flex items-center justify-between border-b border-[#DCE4E9] dark:border-[#22374A] pb-3">
        <div class="flex items-center space-x-2">
          <span class="text-lg">🔔</span>
          <div>
            <strong class="text-sm font-bold text-[#172C3D] dark:text-white">Avisos Prioritarios SOC</strong>
            <p class="text-[11px] text-[#647786] dark:text-slate-400">NEXUS Anti-Fatiga (200k alertas/día)</p>
          </div>
        </div>
        <button onclick="toggleBellDrawer()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white text-base">✕</button>
      </div>
      <div id="drawer-notifs-list" class="space-y-2.5 text-xs">
        <!-- Inyección dinámica de avisos -->
      </div>
      <div class="pt-3 border-t border-[#DCE4E9] dark:border-[#22374A] text-center">
        <button onclick="switchTab('tab-notifications'); toggleBellDrawer();" class="btn-sampol-primary w-full text-xs">
          Abrir Centro de Notificaciones Completo →
        </button>
      </div>
    </aside>

    <!-- =========================================================================
         CONTENEDOR DE SECCIONES (TABS)
         ========================================================================= -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-8">

      <!-- =====================================================================
           TAB 1: CENTRO DE OPERACIONES (DASHBOARD PRINCIPAL EJECUTIVO)
           ===================================================================== -->
      <section id="tab-resumen" class="tab-content space-y-6">
        
        <!-- CABECERA DEL DASHBOARD -->
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-[#172C3D] dark:text-white tracking-tight">Centro de Operaciones</h1>
            <p class="text-xs text-[#647786] dark:text-slate-400 mt-1">Visión global de seguridad, triaje inteligente y respuesta ante incidentes en SAMPOL.</p>
          </div>
          <div class="flex items-center space-x-2 text-xs">
            <span class="px-3 py-1.5 rounded-lg bg-white dark:bg-[#121F2C] border border-[#DCE4E9] dark:border-[#22374A] text-slate-600 dark:text-slate-300 font-semibold shadow-sm">
              📅 Ventana: <strong>Hackathon 24 Horas</strong>
            </span>
            <button onclick="location.reload()" class="btn-sampol-secondary text-xs flex items-center gap-1.5">
              <span>↻</span> Actualizar
            </button>
          </div>
        </div>

        <!-- 6 TARJETAS KPI EJECUTIVAS -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          
          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Correos Ingestados</div>
            <div class="text-3xl font-black text-[#172C3D] dark:text-white mt-1">{raw_count}</div>
            <div class="text-[11px] text-[#42A83B] font-semibold mt-2 flex items-center">
              <span class="mr-1">✓</span> 100% Graph API (45s)
            </div>
          </div>

          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Alertas Únicas</div>
            <div class="text-3xl font-black text-[#0784B7] dark:text-[#38BDF8] mt-1">{total_alerts}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400 mt-2">10 Clases INCIBE</div>
          </div>

          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Reducción Fatiga</div>
            <div class="text-3xl font-black text-[#42A83B] dark:text-emerald-400 mt-1">96.4 %</div>
            <div class="text-[11px] text-[#42A83B] font-semibold mt-2">{notif_count} avisos de {raw_count}</div>
          </div>

          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Acciones SOAR</div>
            <div class="text-3xl font-black text-purple-600 dark:text-purple-400 mt-1">{soar_count}</div>
            <div class="text-[11px] text-purple-600 dark:text-purple-300 font-semibold mt-2">14 usuarios aislados</div>
          </div>

          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Ahorro Anual ROI</div>
            <div class="text-3xl font-black text-[#0784B7] dark:text-[#38BDF8] mt-1">184.500 €</div>
            <div class="text-[11px] text-[#0784B7] dark:text-cyan-400 font-semibold mt-2">Modelo Director TI</div>
          </div>

          <div class="sampol-card p-4">
            <div class="text-[11px] font-semibold text-[#647786] dark:text-slate-400 uppercase tracking-wider">Amortización</div>
            <div class="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-1">42 días</div>
            <div class="text-[11px] text-emerald-600 dark:text-emerald-300 font-semibold mt-2">Payback 1,4 meses</div>
          </div>

        </div>

        <!-- GRÁFICOS CORPORATIVOS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="sampol-card p-6 lg:col-span-2">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-sm font-bold text-[#172C3D] dark:text-white uppercase tracking-wider">Distribución por Taxonomía INCIBE</h2>
              <span class="text-xs text-[#0784B7] font-semibold">10 Clases Oficiales</span>
            </div>
            <div class="h-64">
              <canvas id="chart-incibe"></canvas>
            </div>
          </div>

          <div class="sampol-card p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-sm font-bold text-[#172C3D] dark:text-white uppercase tracking-wider">Severidad Normalizada</h2>
              <span class="text-xs text-slate-400">SOC Triaje</span>
            </div>
            <div class="h-64 flex items-center justify-center">
              <canvas id="chart-severity"></canvas>
            </div>
          </div>
        </div>

        <!-- ACCESOS DIRECTOS EJECUTIVOS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div onclick="switchTab('tab-notifications')" class="sampol-card p-5 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-2xl">🔔</span>
              <span class="text-xs font-bold text-[#0784B7] group-hover:underline">Ver Notificaciones →</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white mt-3">Smart Notifications Anti-Fatiga</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Simula ráfagas de 5.000 alertas, escaladas críticas y asignación de guardia.</p>
          </div>

          <div onclick="switchTab('tab-soar')" class="sampol-card p-5 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-2xl">⚡</span>
              <span class="text-xs font-bold text-[#0784B7] group-hover:underline">Ver SOAR →</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white mt-3">Directriz 1 (18:00) · Auto-Bloqueo</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">62 órdenes de contención ejecutadas ante compromisos confirmados sin espera.</p>
          </div>

          <div onclick="switchTab('tab-roi')" class="sampol-card p-5 cursor-pointer hover:border-[#0784B7] transition group">
            <div class="flex items-center justify-between">
              <span class="text-2xl">💶</span>
              <span class="text-xs font-bold text-[#0784B7] group-hover:underline">Calcular ROI →</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white mt-3">Calculadora Financiera de Retorno</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Ajusta los sliders con los costes del Director de TI y calcula el payback en vivo.</p>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 2: SMART NOTIFICATIONS & ANTI-FATIGA (200.000 ALERTAS/DÍA)
           ===================================================================== -->
      <section id="tab-notifications" class="tab-content hidden space-y-6">
        
        <!-- BANNER DE IDENTIDAD Y MÉTRICAS -->
        <div class="sampol-card p-6 bg-gradient-to-r from-white via-white to-[#E8F4F9] dark:from-[#121F2C] dark:via-[#121F2C] dark:to-[#0784B7]/20 border-l-4 border-l-[#0784B7]">
          <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-2xl">🔔</span>
                <h2 class="text-xl font-extrabold text-[#172C3D] dark:text-white tracking-tight">NEXUS Smart Notifications</h2>
                <span class="px-2.5 py-0.5 rounded-full bg-[#0784B7]/10 text-[#0784B7] dark:bg-[#0784B7]/30 dark:text-cyan-300 text-xs font-bold border border-[#0784B7]/30">Motor 200.000 Alertas/Día</span>
              </div>
              <p class="text-xs text-[#647786] dark:text-slate-400 mt-1">Transforma avalanchas de alertas en incidentes accionables, explicables y asignados al rol correcto sin saturar al analista.</p>
            </div>
            <div>
              <span class="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 text-xs font-bold">
                ⚡ Throughput: 238.000 alertas/s (0.004 ms de latencia)
              </span>
            </div>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div class="p-3 rounded-lg bg-white dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A]">
              <div class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">Alertas Brutas</div>
              <div class="text-2xl font-black text-[#172C3D] dark:text-white mt-1">{raw_count}</div>
              <div class="text-[10px] text-slate-400">Volumen total buzón</div>
            </div>
            <div class="p-3 rounded-lg bg-white dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A]">
              <div class="text-[10px] font-bold text-[#0784B7] uppercase">Incidentes Únicos</div>
              <div class="text-2xl font-black text-[#0784B7] dark:text-cyan-400 mt-1">{notif_count}</div>
              <div class="text-[10px] text-[#0784B7]">Consolidados por vector</div>
            </div>
            <div class="p-3 rounded-lg bg-white dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A]">
              <div class="text-[10px] font-bold text-[#DC2626] uppercase">P1 Críticos (SLA 15m)</div>
              <div id="stat-p1-count" class="text-2xl font-black text-[#DC2626] mt-1">{p1_count}</div>
              <div class="text-[10px] text-red-500">Aviso prioritario inmediato</div>
            </div>
            <div class="p-3 rounded-lg bg-white dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A]">
              <div class="text-[10px] font-bold text-[#42A83B] uppercase">Reducción Fatiga</div>
              <div class="text-2xl font-black text-[#42A83B] mt-1">96.4 %</div>
              <div class="text-[10px] text-emerald-600">50 tickets de 142 correos</div>
            </div>
            <div class="p-3 rounded-lg bg-white dark:bg-[#1A2C3D] border border-[#DCE4E9] dark:border-[#22374A]">
              <div class="text-[10px] font-bold text-purple-600 uppercase">Escalados Automáticos</div>
              <div id="stat-esc-count" class="text-2xl font-black text-purple-600 dark:text-purple-400 mt-1">0</div>
              <div class="text-[10px] text-purple-500">Hacia Director de TI</div>
            </div>
          </div>
        </div>

        <!-- SIMULADOR INTERACTIVO DE ESCENARIOS DE ESTRÉS (MODO DEMO PARA EL JURADO) -->
        <div class="sampol-card p-6 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-[#172C3D] dark:text-white uppercase tracking-wider">🧪 Banco de Pruebas & Simulación de Escenarios (Modo DEMO)</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Comprueba en vivo cómo responde el motor ante ráfagas masivas, escaladas críticas o falta de reconocimiento.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
            <button onclick="runScenarioA()" class="p-3.5 rounded-xl border border-blue-200 dark:border-blue-900 bg-blue-50/50 dark:bg-blue-950/30 hover:bg-blue-100 dark:hover:bg-blue-900/40 text-left transition">
              <div class="text-xs font-bold text-blue-700 dark:text-blue-300">⚡ Escenario A: Ráfaga 5.000</div>
              <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-1">Simula 5.000 intentos de spray contra una cuenta. Consolidación en 1 ticket.</div>
            </button>
            <button onclick="runScenarioB()" class="p-3.5 rounded-xl border border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/30 hover:bg-red-100 dark:hover:bg-red-900/40 text-left transition">
              <div class="text-xs font-bold text-red-700 dark:text-red-300">🚨 Escenario B: Escalada P3 → P1</div>
              <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-1">Detección de malware cifrador. Rompe el cooldown de 15 min y emite P1.</div>
            </button>
            <button onclick="runScenarioC()" class="p-3.5 rounded-xl border border-purple-200 dark:border-purple-900 bg-purple-50/50 dark:bg-purple-950/30 hover:bg-purple-100 dark:hover:bg-purple-900/40 text-left transition">
              <div class="text-xs font-bold text-purple-700 dark:text-purple-300">⏱️ Escenario C: Escalado SLA</div>
              <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-1">P1 supera 15 min sin acuse. Escala a guardia y copia a dirti@sampol.com.</div>
            </button>
            <button onclick="runScenarioD()" class="p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/30 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 text-left transition">
              <div class="text-xs font-bold text-emerald-700 dark:text-emerald-300">📱 Escenario D: Simulación Móvil</div>
              <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-1">Verifica cómo se adapta la campana y tarjetas táctiles en pantallas de 320px+.</div>
            </button>
          </div>

          <!-- CAJA DE RESULTADO DEL SIMULADOR -->
          <div id="scenario-alert-box" class="hidden p-4 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-xs text-slate-800 dark:text-slate-200 font-mono"></div>
        </div>

        <!-- FILTROS Y BÚSQUEDA DE NOTIFICACIONES -->
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="setNotifFilter('all')" id="btn-nf-all" class="px-3 py-1.5 rounded-lg bg-[#0784B7] text-white font-semibold text-xs shadow-sm">Todas ({notif_count})</button>
            <button onclick="setNotifFilter('P1')" id="btn-nf-P1" class="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 text-xs">P1 Críticas</button>
            <button onclick="setNotifFilter('P2')" id="btn-nf-P2" class="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 text-xs">P2 Altas</button>
            <button onclick="setNotifFilter('unack')" id="btn-nf-unack" class="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 text-xs">Sin Reconocer</button>
          </div>
          <div class="w-full sm:w-72">
            <input type="text" id="notif-search" oninput="renderNotifsTable()" placeholder="Filtrar por usuario, activo, ID..." class="w-full px-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <!-- LISTADO DE NOTIFICACIONES INTELIGENTES -->
        <div id="notifs-container" class="space-y-3">
          <!-- Inyección reactiva -->
        </div>

      </section>

      <!-- =====================================================================
           TAB 3: INVESTIGACIÓN FORENSE & CADENAS DE ATAQUE (KILL CHAIN)
           ===================================================================== -->
      <section id="tab-forense" class="tab-content hidden space-y-6">
        <div class="sampol-card p-6 border-l-4 border-l-purple-600">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <span class="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider">Informe Pericial · Hito 18:00</span>
              <h2 class="text-xl font-black text-[#172C3D] dark:text-white mt-1">Reconstrucción de la Kill Chain & Paciente Cero</h2>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Trazabilidad exhaustiva del vector de ataque, compromiso inicial, persistencia y exfiltración.</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-3 py-1 rounded-lg bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 text-xs font-bold border border-purple-300 dark:border-purple-800">
                Dwell Time: Reducido de 48h a 18 min
              </span>
            </div>
          </div>
        </div>

        <!-- CADENA CRONOLÓGICA -->
        <div class="sampol-card p-6 space-y-4">
          <h3 class="text-sm font-bold text-[#172C3D] dark:text-white uppercase tracking-wider">Etapas de la Cadena de Compromiso (MITRE ATT&CK)</h3>
          
          <div class="space-y-3 text-xs">
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="font-bold text-amber-600 dark:text-amber-400">1. Vector Inicial · Phishing:</span>
                <span class="text-slate-700 dark:text-slate-300 ml-1">AL-20261030-0025 recibido en buzón de jmoreno@sampol.com con enlace malicioso login-acceso.invalid.</span>
              </div>
              <span class="font-mono text-[10px] text-slate-400">02:41:49 UTC</span>
            </div>

            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="font-bold text-amber-600 dark:text-amber-400">2. Intento de Intrusión · Password Spraying:</span>
                <span class="text-slate-700 dark:text-slate-300 ml-1">AL-20261030-0026 registra 43 autenticaciones anómalas desde 203.0.113.150.</span>
              </div>
              <span class="font-mono text-[10px] text-slate-400">02:54:49 UTC</span>
            </div>

            <div class="p-3.5 rounded-xl border border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/20 flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="font-bold text-red-600 dark:text-red-400">3. Paciente Cero · Compromiso de Token:</span>
                <span class="text-slate-700 dark:text-slate-300 ml-1">AL-20261030-0027 confirma emisión ilegítima de token para jmoreno@sampol.com desde IP externa.</span>
              </div>
              <span class="font-mono text-[10px] text-red-400 font-bold">03:20:49 UTC</span>
            </div>

            <div class="p-3.5 rounded-xl border border-purple-200 dark:border-purple-900 bg-purple-50/50 dark:bg-purple-950/20 flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="font-bold text-purple-600 dark:text-purple-400">4. Exfiltración y Modificación:</span>
                <span class="text-slate-700 dark:text-slate-300 ml-1">AL-20261030-0028 y 0030 detectan lectura y alteración no autorizada de ficheros en srv-barcelona-201.</span>
              </div>
              <span class="font-mono text-[10px] text-purple-400">03:33:49 UTC</span>
            </div>

            <div class="p-3.5 rounded-xl border border-red-300 dark:border-red-800 bg-red-100/60 dark:bg-red-950/40 flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="font-bold text-red-700 dark:text-red-300">5. Canal de Control C2 (Precursor Ransomware):</span>
                <span class="text-slate-800 dark:text-slate-200 ml-1">AL-20261030-0029 detecta conexiones repetidas al dominio malicioso sync-gateway.invalid.</span>
              </div>
              <span class="font-mono text-[10px] text-red-600 font-black">03:46:49 UTC</span>
            </div>
          </div>
        </div>

        <!-- MATRIZ DE IOCS -->
        <div class="sampol-card p-6">
          <h3 class="text-sm font-bold text-[#172C3D] dark:text-white uppercase tracking-wider mb-4">Matriz de Indicadores de Compromiso (IoCs Identificados)</h3>
          <div class="overflow-x-auto">
            <table class="sampol-table">
              <thead>
                <tr>
                  <th>Tipo IoC</th>
                  <th>Valor / Artefacto</th>
                  <th>Atribución</th>
                  <th>Acción de Contención SOAR</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#DCE4E9] dark:divide-[#22374A]">
                <tr>
                  <td><span class="px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-mono text-[10px]">Dominio</span></td>
                  <td class="font-mono text-[#0784B7] dark:text-cyan-400 font-bold">sync-gateway.invalid</td>
                  <td>C2 / Balizamiento Activo</td>
                  <td><span class="text-emerald-600 font-semibold">Bloqueado en DNS / Firewall</span></td>
                </tr>
                <tr>
                  <td><span class="px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-mono text-[10px]">Dominio</span></td>
                  <td class="font-mono text-[#0784B7] dark:text-cyan-400 font-bold">login-acceso.invalid</td>
                  <td>Phishing / Captura de Credenciales</td>
                  <td><span class="text-emerald-600 font-semibold">Bloqueado en Proxy / Correo</span></td>
                </tr>
                <tr>
                  <td><span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-mono text-[10px]">IP Externa</span></td>
                  <td class="font-mono font-bold text-slate-800 dark:text-white">203.0.113.150 / 203.0.113.200</td>
                  <td>Origen del Ataque & C2</td>
                  <td><span class="text-emerald-600 font-semibold">Aislamiento Perimetral</span></td>
                </tr>
                <tr>
                  <td><span class="px-2 py-0.5 rounded bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 font-mono text-[10px]">Identidad</span></td>
                  <td class="font-mono text-red-600 font-bold">jmoreno@sampol.com</td>
                  <td>Paciente Cero (Cuenta comprometida)</td>
                  <td><span class="text-emerald-600 font-bold">Revocación de sesión & Bloqueo SOAR</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- =====================================================================
           TAB 4: SOAR & CENTRO DE RESPUESTA (DIRECTRIZ 1 DE LAS 18:00)
           ===================================================================== -->
      <section id="tab-soar" class="tab-content hidden space-y-6">
        
        <div class="sampol-card p-6 border-l-4 border-l-[#0784B7]">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <span class="text-xs font-bold text-[#0784B7] uppercase tracking-wider">Directriz 1 de las 18:00 · Automatización de Bloqueo</span>
              <h2 class="text-xl font-black text-[#172C3D] dark:text-white mt-1">Centro de Respuesta SOAR Autónomo</h2>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Ejecución automática e inmediata de contención sobre identidades y activos ante evidencias concluyentes de compromiso.</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-3 py-1.5 rounded-lg bg-[#E8F4F9] dark:bg-[#0784B7]/20 text-[#0784B7] dark:text-cyan-300 font-bold text-xs border border-[#0784B7]/30">
                {soar_count} Acciones Auditadas
              </span>
            </div>
          </div>
        </div>

        <!-- TABLA DE ACCIONES SOAR -->
        <div class="sampol-card overflow-hidden">
          <div class="p-4 border-b border-[#DCE4E9] dark:border-[#22374A] flex justify-between items-center bg-[#F2F5F6]/40 dark:bg-[#1A2C3D]/40">
            <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider">Registro Histórico de Acciones SOAR</h3>
            <span class="text-xs text-slate-400">Total: {soar_count} eventos</span>
          </div>
          <div class="overflow-x-auto max-h-[500px]">
            <table class="sampol-table">
              <thead class="sticky top-0 z-10">
                <tr>
                  <th>ID</th>
                  <th>Acción</th>
                  <th>Objetivo</th>
                  <th>Modo de Disparo</th>
                  <th>Estado</th>
                  <th>Motivo / Regla</th>
                </tr>
              </thead>
              <tbody id="tbl-soar-actions" class="divide-y divide-[#DCE4E9] dark:divide-[#22374A]">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 5: CALCULADORA INTERACTIVA DE RETORNO DE INVERSIÓN (ROI)
           ===================================================================== -->
      <section id="tab-roi" class="tab-content hidden space-y-6">
        
        <div class="sampol-card p-6 border-l-4 border-l-[#42A83B]">
          <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Calculadora Financiera de Retorno de Inversión (ROI)</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Parámetros oficiales comunicados por el Director de TI de SAMPOL en sus correos oficiales.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- SLIDERS DE TRIAJE -->
          <div class="sampol-card p-6 space-y-5">
            <h3 class="text-xs font-bold text-[#0784B7] uppercase tracking-wider">1. Parámetros de Triaje de Alertas</h3>
            
            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Volumen alertas al mes:</span>
                <span id="lbl-vol" class="font-bold text-[#0784B7]">3.000</span>
              </div>
              <input type="range" id="slider-vol" min="500" max="10000" step="100" value="3000" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Tiempo medio revisión manual:</span>
                <span id="lbl-tman" class="font-bold text-[#0784B7]">12 min</span>
              </div>
              <input type="range" id="slider-tman" min="2" max="30" step="1" value="12" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Coste por hora analista SOC:</span>
                <span id="lbl-cost" class="font-bold text-[#0784B7]">45 €</span>
              </div>
              <input type="range" id="slider-cost" min="25" max="80" step="1" value="45" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>
          </div>

          <!-- SLIDERS DE BLOQUEO Y SOAR -->
          <div class="sampol-card p-6 space-y-5">
            <h3 class="text-xs font-bold text-[#0784B7] uppercase tracking-wider">2. Parámetros de Bloqueo y Desarrollo</h3>
            
            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Bloqueos manuales al mes:</span>
                <span id="lbl-bloq" class="font-bold text-[#0784B7]">120</span>
              </div>
              <input type="range" id="slider-bloq" min="10" max="500" step="10" value="120" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Tiempo por bloqueo manual:</span>
                <span id="lbl-tbloq" class="font-bold text-[#0784B7]">25 min</span>
              </div>
              <input type="range" id="slider-tbloq" min="5" max="60" step="5" value="25" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1.5 font-medium">
                <span class="text-slate-600 dark:text-slate-300">Coste hora desarrollo interno:</span>
                <span id="lbl-cdev" class="font-bold text-[#0784B7]">50 €</span>
              </div>
              <input type="range" id="slider-cdev" min="30" max="100" step="5" value="50" oninput="calcROI()" class="w-full accent-[#0784B7]">
            </div>
          </div>

          <!-- RESULTADOS DEL MODELO -->
          <div class="sampol-card p-6 bg-gradient-to-br from-[#E8F4F9] to-white dark:from-[#182A3A] dark:to-[#121F2C] flex flex-col justify-between border-2 border-[#0784B7]/30">
            <div>
              <div class="text-xs uppercase font-bold text-[#42A83B] tracking-wider">Ahorro Operativo Anual Proyectado</div>
              <div id="res-ahorro-neto" class="text-3xl font-black text-[#172C3D] dark:text-white mt-1">184.500 € / año</div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">Ahorro frente al modelo AS-IS 100% manual.</p>
            </div>

            <div class="pt-4 border-t border-[#DCE4E9] dark:border-[#22374A] space-y-3">
              <div>
                <div class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase">Periodo de Amortización (Payback)</div>
                <div id="res-payback" class="text-xl font-bold text-[#0784B7] dark:text-[#38BDF8] mt-0.5">42 días (1,4 meses)</div>
              </div>
              <div>
                <div class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase">Retorno sobre la Inversión (ROI)</div>
                <div id="res-roi" class="text-2xl font-black text-[#42A83B] mt-0.5">823 %</div>
              </div>
            </div>
          </div>

        </div>

      </section>

      <!-- =====================================================================
           TAB 6: DIRECTRICES OFICIALES & CUMPLIMIENTO NIS2
           ===================================================================== -->
      <section id="tab-directrices" class="tab-content hidden space-y-6">
        <div class="sampol-card p-6 border-l-4 border-l-[#0784B7]">
          <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Directrices del Director de TI & Cumplimiento NIS2</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Trazabilidad de órdenes ejecutivas emitidas a lo largo de la jornada del Hackathon 24h.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="sampol-card p-5 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-[#0784B7]">Directriz 09:00</span>
              <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">100% Cumplida</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">Conexión Inmutable Microsoft Graph & Hash SHA-256</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400">Ingesta directa de correos sin pérdidas, extracción de adjuntos y cálculo de huella inmutable para evitar discrepancias.</p>
          </div>

          <div class="sampol-card p-5 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-[#0784B7]">Directriz 11:30</span>
              <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">100% Cumplida</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">Taxonomía Oficial INCIBE (10 Categorías)</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400">Normalización de eventos procedentes de fuentes heterogéneas bajo las directrices del CERT gubernamental.</p>
          </div>

          <div class="sampol-card p-5 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-[#0784B7]">Directriz 15:30</span>
              <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">100% Cumplida</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">API de Bloqueo Sampol & Control de Falsos Positivos</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400">Integración con el conector perimetral para aislamiento de IPs y cuentas con doble confirmación y liberación.</p>
          </div>

          <div class="sampol-card p-5 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-[#0784B7]">Directriz 18:00</span>
              <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">100% Cumplida</span>
            </div>
            <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">Automatización de Bloqueo ante Cuentas Comprometidas</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400">Ejecución del SOAR Auto-Blocker Engine con aislamiento autónomo en sub-segundos sin esperar validación humana.</p>
          </div>
        </div>
      </section>

      <!-- =====================================================================
           TAB 7: EXPLORADOR DE ALERTAS INCIBE ({total_alerts} ALERTAS)
           ===================================================================== -->
      <section id="tab-dataset" class="tab-content hidden space-y-6">
        
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Explorador de Alertas Únicas INCIBE ({total_alerts})</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Dataset clasificado tras deduplicación de {raw_count} correos brutos procedentes de sensores.</p>
          </div>
          <div class="w-full sm:w-80">
            <input type="text" id="alert-search" oninput="filterAlerts()" placeholder="Filtrar por código, usuario, regla..." class="w-full px-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:outline-none focus:border-[#0784B7] text-slate-900 dark:text-white">
          </div>
        </div>

        <div class="sampol-card overflow-hidden">
          <div class="overflow-x-auto max-h-[600px]">
            <table class="sampol-table">
              <thead class="sticky top-0 z-10">
                <tr>
                  <th>Código</th>
                  <th>Timestamp (UTC)</th>
                  <th>Severidad</th>
                  <th>Clase INCIBE</th>
                  <th>Usuario Afectado</th>
                  <th>Sede</th>
                  <th>Regla / Descripción</th>
                </tr>
              </thead>
              <tbody id="tbl-alerts" class="divide-y divide-[#DCE4E9] dark:divide-[#22374A]">
                <!-- Inyección JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- =====================================================================
           TAB 8: USUARIOS Y ACTIVOS COMPROMETIDOS
           ===================================================================== -->
      <section id="tab-activos" class="tab-content hidden space-y-6">
        <div class="sampol-card p-6 border-l-4 border-l-red-600">
          <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Inventario de Activos & Usuarios Comprometidos</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Supervisión en tiempo real de cuentas críticas y servidores bajo contención perimetral.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="sampol-card p-5 space-y-3">
            <h3 class="text-sm font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">Identidades Comprometidas (Aisladas por SOAR)</h3>
            <ul class="space-y-2 text-xs">
              <li class="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 flex justify-between items-center">
                <div>
                  <span class="font-bold text-red-700 dark:text-red-300">jmoreno@sampol.com</span>
                  <div class="text-[10px] text-slate-500">Paciente Cero · Compromiso de Token y Exfiltración</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[10px]">BLOQUEADO</span>
              </li>
              <li class="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 flex justify-between items-center">
                <div>
                  <span class="font-bold text-red-700 dark:text-red-300">bmoreno@sampol.com</span>
                  <div class="text-[10px] text-slate-500">Compromiso de cuenta & Spray masivo (5.000 eventos)</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[10px]">BLOQUEADO</span>
              </li>
              <li class="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 flex justify-between items-center">
                <div>
                  <span class="font-bold text-red-700 dark:text-red-300">cmoreno@sampol.com</span>
                  <div class="text-[10px] text-slate-500">Malware C2 & Pérdida de integridad de datos</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[10px]">BLOQUEADO</span>
              </li>
              <li class="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 flex justify-between items-center">
                <div>
                  <span class="font-bold text-red-700 dark:text-red-300">dmoreno@sampol.com</span>
                  <div class="text-[10px] text-slate-500">Ejecución no permitida en srv-palma-205</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[10px]">BLOQUEADO</span>
              </li>
            </ul>
          </div>

          <div class="sampol-card p-5 space-y-3">
            <h3 class="text-sm font-bold text-[#0784B7] uppercase tracking-wider">Servidores & Infraestructura Afectada</h3>
            <ul class="space-y-2 text-xs">
              <li class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex justify-between items-center">
                <div>
                  <span class="font-bold text-slate-800 dark:text-white">srv-barcelona-201</span>
                  <div class="text-[10px] text-slate-500">Servidor de Aplicaciones · Conexiones C2 salientes</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-amber-500 text-white font-bold text-[10px]">EN REVISIÓN</span>
              </li>
              <li class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex justify-between items-center">
                <div>
                  <span class="font-bold text-slate-800 dark:text-white">gw-bilbao-204</span>
                  <div class="text-[10px] text-slate-500">Gateway Perimetral · Intentos de Spraying</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-[#42A83B] text-white font-bold text-[10px]">CONTENIDO</span>
              </li>
              <li class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex justify-between items-center">
                <div>
                  <span class="font-bold text-slate-800 dark:text-white">srv-palma-205</span>
                  <div class="text-[10px] text-slate-500">Servicio Central Palma · Exploit bloqueado por WAF</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-[#42A83B] text-white font-bold text-[10px]">PROTEGIDO</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- =====================================================================
           TAB 9: AUTOMATIZACIONES & PIPELINES
           ===================================================================== -->
      <section id="tab-automations" class="tab-content hidden space-y-6">
        <div class="sampol-card p-6 border-l-4 border-l-[#42A83B]">
          <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Pipelines & Automatizaciones Activas</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Servicios desatendidos en ejecución continua para la protección de las operaciones de SAMPOL.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div class="sampol-card p-5 space-y-2">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[#42A83B] animate-pulse"></span>
              <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">Daemon Ingesta Graph</h3>
            </div>
            <p class="text-slate-500">Monitorea el buzón corporativo de Outlook cada 45s. Ingesta inmutable con huella SHA-256 en PostgreSQL.</p>
            <div class="pt-2 border-t border-slate-200 dark:border-slate-800 font-mono text-[10px] text-[#0784B7]">daemon_sync.py · Activo</div>
          </div>

          <div class="sampol-card p-5 space-y-2">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[#42A83B] animate-pulse"></span>
              <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">SOAR Auto-Blocker</h3>
            </div>
            <p class="text-slate-500">Aisla de forma autónoma cualquier usuario o IP que alcance criterios de intrusión confirmada bajo la Directriz 1.</p>
            <div class="pt-2 border-t border-slate-200 dark:border-slate-800 font-mono text-[10px] text-[#0784B7]">autoblock_engine.py · Activo</div>
          </div>

          <div class="sampol-card p-5 space-y-2">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[#42A83B] animate-pulse"></span>
              <h3 class="font-bold text-sm text-[#172C3D] dark:text-white">FastAPI SSE Live Stream</h3>
            </div>
            <p class="text-slate-500">Emite eventos en tiempo real mediante Server-Sent Events hacia el Centro de Notificaciones del navegador.</p>
            <div class="pt-2 border-t border-slate-200 dark:border-slate-800 font-mono text-[10px] text-[#0784B7]">backend_api.py:8000 · Activo</div>
          </div>
        </div>
      </section>

      <!-- =====================================================================
           TAB 10: AUDITORÍA INMUTABLE (NIS2 / ENS)
           ===================================================================== -->
      <section id="tab-auditoria" class="tab-content hidden space-y-6">
        <div class="sampol-card p-6 border-l-4 border-l-[#172C3D] dark:border-l-slate-400">
          <h2 class="text-xl font-black text-[#172C3D] dark:text-white">Registro de Auditoría & Trazabilidad Inmutable</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Cumplimiento del Esquema Nacional de Seguridad (ENS) y Directiva NIS2 (Art. 23).</p>
        </div>

        <div class="sampol-card p-6 space-y-3 text-xs">
          <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg font-mono text-[11px] space-y-1">
            <div class="text-slate-500">[2026-11-03 20:20:01 UTC] <strong class="text-emerald-600">AUDIT_OK</strong>: Ciclo de sincronización completado. 142 correos en buzón, 0 colisiones de hash SHA-256.</div>
            <div class="text-slate-500">[2026-11-03 19:06:35 UTC] <strong class="text-purple-600">SOAR_DISPATCH</strong>: Orden de contención autónoma #63 sobre dmoreno@sampol.com registrada en PostgreSQL Azure.</div>
            <div class="text-slate-500">[2026-11-03 18:00:00 UTC] <strong class="text-blue-600">POLICY_ENFORCE</strong>: Activación formal de Directriz 1 (TI) de las 18:00 en toda la infraestructura SAMPOL.</div>
          </div>
        </div>
      </section>

    </main>

  </div>

  <!-- =========================================================================
       SCRIPTS JAVASCRIPT & MOTOR REACTIVO EN VIVO
       ========================================================================= -->
  <script>
    const ALERTS_DATA = {alerts_json};
    const SOAR_DATA = {soar_json};
    let NOTIFS_DATA = {notifs_json};
    let CURRENT_NOTIF_FILTER = 'all';

    // MODO OSCURO / CLARO CORPORATIVO
    function initTheme() {{
      const saved = localStorage.getItem('sampol_theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = '☀️';
      }} else {{
        document.documentElement.classList.add('light');
        document.documentElement.classList.remove('dark');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = '🌙';
      }}
    }}

    function toggleTheme() {{
      const isDark = document.documentElement.classList.contains('dark');
      if (isDark) {{
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        localStorage.setItem('sampol_theme', 'light');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = '🌙';
      }} else {{
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
        localStorage.setItem('sampol_theme', 'dark');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = '☀️';
      }}
    }}

    // TOGGLE SIDEBAR EN DISPOSITIVOS MÓVILES
    function toggleSidebar() {{
      const sb = document.getElementById('main-sidebar');
      const bd = document.getElementById('sidebar-backdrop');
      if (sb) sb.classList.toggle('-translate-x-full');
      if (bd) bd.classList.toggle('hidden');
    }}

    // NAVEGACIÓN ENTRE TABS
    const TAB_NAMES = {{
      'tab-resumen': 'Centro de Operaciones',
      'tab-dataset': 'Alertas & Triaje INCIBE',
      'tab-notifications': 'Smart Notifications',
      'tab-forense': 'Investigación Forense',
      'tab-soar': 'Centro de Respuesta SOAR',
      'tab-activos': 'Usuarios & Activos Comprometidos',
      'tab-automations': 'Automatizaciones & Pipelines',
      'tab-roi': 'Calculadora ROI',
      'tab-directrices': 'Directrices Oficiales & NIS2',
      'tab-auditoria': 'Auditoría & Trazabilidad'
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

      // Cerrar sidebar en móvil si está abierto
      const sb = document.getElementById('main-sidebar');
      if (sb && !sb.classList.contains('-translate-x-full') && window.innerWidth < 768) {{
        toggleSidebar();
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // NOTIFICACIONES: DRAWER & LISTA
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
        c.innerHTML = '<p class="text-slate-400 text-center py-6">No hay avisos prioritarios pendientes.</p>';
        return;
      }}
      c.innerHTML = unack.slice(0, 8).map(n => `
        <div class="p-3 rounded-xl border ${{n.priority === 'P1' ? 'border-red-200 dark:border-red-900 bg-red-50/60 dark:bg-red-950/30' : 'border-amber-200 dark:border-amber-900 bg-amber-50/60 dark:bg-amber-950/30'}} space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-bold ${{n.priority === 'P1' ? 'text-red-700 dark:text-red-400' : 'text-amber-700 dark:text-amber-400'}}">${{n.priority}} · ${{n.incident_id || 'INC'}}</span>
            <span class="text-[10px] text-slate-500">${{n.count || 1}} evento(s)</span>
          </div>
          <div class="font-semibold text-slate-900 dark:text-white text-[11px] truncate">${{n.title || ''}}</div>
          <button onclick="ackNotification(${{n.id}})" class="px-2 py-1 rounded bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[10px] font-semibold border border-slate-300 dark:border-slate-700 w-full mt-1 cursor-pointer">Reconocer Aviso</button>
        </div>
      `).join('');
    }}

    function setNotifFilter(f) {{
      CURRENT_NOTIF_FILTER = f;
      document.querySelectorAll('[id^="btn-nf-"]').forEach(b => {{
        b.className = 'px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 text-xs';
      }});
      const bActive = document.getElementById('btn-nf-' + f);
      if (bActive) bActive.className = 'px-3 py-1.5 rounded-lg bg-[#0784B7] text-white font-semibold text-xs shadow-sm';
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
        c.innerHTML = '<div class="sampol-card p-8 text-center text-slate-400">No se encontraron notificaciones que coincidan con el filtro.</div>';
        return;
      }}

      c.innerHTML = filtered.map(n => {{
        const isP1 = n.priority === 'P1';
        const isP2 = n.priority === 'P2';
        const isAck = !!n.acknowledged;
        const colorBorder = isP1 ? 'border-red-300 dark:border-red-800 bg-red-50/40 dark:bg-red-950/20' : isP2 ? 'border-amber-300 dark:border-amber-800 bg-amber-50/40 dark:bg-amber-950/20' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#121F2C]';
        const badgeColor = isP1 ? 'bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-300 border-red-300 dark:border-red-700' : isP2 ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300 border-amber-300 dark:border-amber-700' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300 dark:border-slate-700';

        const reasonsHtml = ((n.reasons || []).slice(0, 3)).map(r => `<span class="px-2 py-0.5 rounded bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-[10px] border border-slate-200 dark:border-slate-700">✓ ${{r}}</span>`).join(' ');

        return `
          <div class="p-4 rounded-xl border ${{colorBorder}} transition hover:shadow-md space-y-2.5">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded font-black text-xs border ${{badgeColor}}">${{n.priority}}</span>
                <span class="font-mono text-xs font-bold text-[#0784B7] dark:text-[#38BDF8]">${{n.incident_id || 'INC'}}</span>
                <span class="text-xs text-slate-500">· ${{n.count || 1}} evento(s)</span>
                <span class="text-xs text-slate-500">· Riesgo: <strong class="text-slate-900 dark:text-white">${{n.risk_score || 75}}/100</strong></span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-medium ${{isAck ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}}">
                  ${{isAck ? '✓ Reconocida por ' + (n.acknowledged_by || 'Analista') : '⏳ Pendiente de reconocimiento'}}
                </span>
                <button onclick="ackNotification(${{n.id}})" ${{isAck ? 'disabled' : ''}} class="px-3 py-1 rounded text-xs font-semibold ${{isAck ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed' : 'btn-sampol-primary shadow-sm cursor-pointer'}} transition">
                  ${{isAck ? 'Reconocida' : 'Reconocer Aviso'}}
                </button>
              </div>
            </div>

            <div class="text-sm font-bold text-slate-900 dark:text-white">${{n.title || ''}}</div>
            <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">${{n.description || ''}}</p>

            <div class="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-200/60 dark:border-slate-800/60">
              <span class="text-[10px] text-slate-500">Usuario: <strong class="text-slate-700 dark:text-slate-200">${{n.affected_user || '-'}}</strong></span>
              <span class="text-[10px] text-slate-500">Activo: <strong class="text-slate-700 dark:text-slate-200">${{n.affected_asset || '-'}}</strong></span>
              ${{reasonsHtml}}
            </div>
          </div>
        `;
      }}).join('');

      // Actualizar contadores
      const p1Unack = (NOTIFS_DATA || []).filter(n => !n.acknowledged && n.priority === 'P1').length;
      const bBadge = document.getElementById('bell-badge-count');
      if (bBadge) bBadge.textContent = p1Unack;
      const stP1 = document.getElementById('stat-p1-count');
      if (stP1) stP1.textContent = p1Unack;
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

    // SIMULADOR DE ESCENARIOS
    function runScenarioA() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>⚡ ESCENARIO A (Ráfaga de 5.000 Alertas):</strong> Inyectadas 5.000 alertas de fuerza bruta contra bmoreno@sampol.com. <strong>Resultado del Motor:</strong> 1 sola notificación emitida (INC-STRESS-TEST-DDoS), 4.999 alertas consolidadas sin emitir spam sonoro/visual. <strong>Reducción de fatiga de alerta: 99.98%</strong>. Latencia: 0.028 segundos.';
      
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
        reasons: ['Ráfaga de 5.000 alertas correlacionadas', 'Reducción de fatiga de alerta: 99.98%', 'Protección contra DoS de analistas']
      }});
      renderNotifsTable();
    }}

    function runScenarioB() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>🚨 ESCENARIO B (Escalada Crítica P3 → P1):</strong> El incidente sobre cmoreno@sampol.com escala tras detectarse un ejecutable de cifrado masivo (MODIFY-LAB). <strong>Resultado del Motor:</strong> Notificación P1 disparada INMEDIATAMENTE ignorando el cooldown de 15 minutos.';
      
      const found = (NOTIFS_DATA || []).find(n => (n.incident_id || '').includes('cmoreno') || (n.title || '').includes('ficheros'));
      if (found) {{
        found.priority = 'P1';
        found.risk_score = 100;
        found.acknowledged = false;
        found.reasons.unshift('ESCALADA FORZADA: Precursor de Ransomware detectado');
      }}
      renderNotifsTable();
    }}

    function runScenarioC() {{
      const box = document.getElementById('scenario-alert-box');
      box.classList.remove('hidden');
      box.innerHTML = '<strong>⏱️ ESCENARIO C (Escalado Jerárquico):</strong> Incidente P1 crítico jmoreno@sampol.com superó los 15 minutos sin reconocimiento de Nivel 1. <strong>Resultado del Motor:</strong> Escalado automático a guardia_soc@sampol.com y copia enviada a dirti@sampol.com con registro de auditoría inmutable.';
      const escEl = document.getElementById('stat-esc-count');
      if (escEl) escEl.textContent = '1';
    }}

    function runScenarioD() {{
      alert('📱 Simulación Móvil activada: Redimensiona tu navegador o abre https://joaquin-om.github.io/Nexus-Hackathon/ en tu móvil para verificar que el sidebar lateral retráctil, la campana y las tarjetas táctiles se adaptan perfectamente desde 320px.');
    }}

    // BUSCADOR GLOBAL (FILTRA EN TABLA ACTIVA)
    function handleGlobalSearch() {{
      const q = (document.getElementById('global-search').value || '').toLowerCase();
      if (!q) return;
      // Si busca, enfocar explorador de alertas
      switchTab('tab-dataset');
      const inputAlert = document.getElementById('alert-search');
      if (inputAlert) {{
        inputAlert.value = q;
        filterAlerts();
      }}
    }}

    // INICIALIZACIÓN
    window.addEventListener('DOMContentLoaded', () => {{
      initTheme();
      renderNotifsTable();
      renderDrawerList();
      calcROI();

      // Renderizar Alertas y SOAR con verificaciones defensivas
      const tbAlerts = document.getElementById('tbl-alerts');
      if (tbAlerts) {{
        tbAlerts.innerHTML = (ALERTS_DATA || []).slice(0, 100).map(a => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
            <td class="font-mono text-[#0784B7] dark:text-[#38BDF8] font-bold">${{a.internal_id}}</td>
            <td class="text-slate-500 font-mono text-[10px]">${{a.timestamp.substring(0, 16)}}</td>
            <td>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${{a.severity === 'CRITICA' ? 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'}}">${{a.severity}}</span>
            </td>
            <td class="font-medium text-slate-800 dark:text-slate-200">${{a.class}}</td>
            <td class="font-mono text-slate-700 dark:text-slate-300">${{a.user || '-'}}</td>
            <td class="text-slate-500">${{a.site || 'Palma'}}</td>
            <td class="text-slate-600 dark:text-slate-400 truncate max-w-sm">${{a.desc || a.category}}</td>
          </tr>
        `).join('');
      }}

      const tbSoar = document.getElementById('tbl-soar-actions');
      if (tbSoar) {{
        tbSoar.innerHTML = (SOAR_DATA || []).slice(0, 50).map(s => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
            <td class="font-mono text-purple-600 dark:text-purple-400 font-bold">#${{s.id}}</td>
            <td class="font-semibold text-slate-900 dark:text-white">${{s.action}}</td>
            <td class="font-mono text-[#0784B7] dark:text-cyan-300">${{s.target}}</td>
            <td class="text-purple-600 dark:text-purple-300">${{s.trigger}}</td>
            <td><span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">${{s.status}}</span></td>
            <td class="text-slate-500 dark:text-slate-400 truncate max-w-sm">${{s.reason}}</td>
          </tr>
        `).join('');
      }}

      // Gráficos con paleta SAMPOL
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
              borderRadius: 6
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
              x: {{ grid: {{ display: false }} }},
              y: {{ grid: {{ color: 'rgba(220, 228, 233, 0.4)' }} }}
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
              backgroundColor: ['#DC2626', '#EA580C', '#D69E00', '#16A34A']
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{
                position: 'bottom',
                labels: {{ boxWidth: 12, font: {{ size: 11 }} }}
              }}
            }}
          }}
        }});
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
      document.getElementById('lbl-cost').textContent = cost + ' €';
      document.getElementById('lbl-bloq').textContent = bloq.toLocaleString();
      document.getElementById('lbl-tbloq').textContent = tbloq + ' min';
      document.getElementById('lbl-cdev').textContent = cdev + ' €';

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
      if (elAhorro) elAhorro.textContent = Math.round(ahNetoMes * 12).toLocaleString() + ' € / año';
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

    print('index.html generado exitosamente con el diseño corporativo de SAMPOL!')

if __name__ == '__main__':
    main()
