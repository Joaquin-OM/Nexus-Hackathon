/* NEXUS SOC notification widget. Standalone, no credentials in frontend. */
(() => {
  const config = window.NEXUS_NOTIFICATIONS || {};
  const apiBase = (config.apiBase || '').replace(/\/$/, '');
  const demo = config.demo !== false;
  const storageKey = 'nexus-smart-notifications-demo-v1';
  const seed = [
    {id:'DEMO-001',incident_id:'INC-042',title:'Posible compromiso de cuenta privilegiada',description:'8 alertas relacionadas; revisar evidencias antes de actuar.',priority:'P1',count:8,acknowledged:false},
    {id:'DEMO-002',incident_id:'INC-041',title:'Actividad anómala en servidor',description:'23 eventos agrupados en una investigación.',priority:'P2',count:23,acknowledged:false},
    {id:'DEMO-003',incident_id:'INC-040',title:'Resumen de actividad informativa',description:'Eventos sin intervención inmediata.',priority:'P3',count:1420,acknowledged:false}
  ];
  let items = []; let filter = 'all';
  const root = document.createElement('div'); root.id='nexus-notifications-root';
  const bell = document.createElement('button'); bell.className='nexus-bell';bell.type='button';bell.setAttribute('aria-label','Abrir notificaciones');bell.setAttribute('aria-expanded','false');bell.textContent='🔔';
  const badge=document.createElement('span');badge.className='nexus-badge';bell.appendChild(badge);
  const panel=document.createElement('section');panel.className='nexus-panel';panel.hidden=true;panel.setAttribute('aria-label','Centro de notificaciones');
  root.append(bell,panel);document.body.appendChild(root);
  function element(tag, cls, content){const el=document.createElement(tag);if(cls)el.className=cls;if(content!==undefined)el.textContent=String(content);return el;}
  function save(){if(demo)localStorage.setItem(storageKey,JSON.stringify(items));}
  async function load(){
    if(demo){try{items=JSON.parse(localStorage.getItem(storageKey))||seed.map(x=>({...x}));}catch{items=seed.map(x=>({...x}));}render();return;}
    try{const r=await fetch(`${apiBase}/api/smart-notifications`,{credentials:'include'});if(!r.ok)throw Error(`HTTP ${r.status}`);const result=await r.json();items=Array.isArray(result)?result:result.items||[];render();}
    catch(e){panel.replaceChildren(element('p','nexus-empty','No se pueden cargar las notificaciones.'));badge.textContent='!';console.error('NEXUS notifications:',e);}
  }
  async function acknowledge(id){
    if(demo){items=items.map(x=>x.id===id?{...x,acknowledged:true}:x);save();render();return;}
    try{const r=await fetch(`${apiBase}/api/smart-notifications/${encodeURIComponent(id)}/acknowledge`,{method:'POST',credentials:'include'});if(!r.ok)throw Error(`HTTP ${r.status}`);await load();}catch(e){alert('No se pudo reconocer el aviso.');console.error(e);}
  }
  function render(){
    badge.textContent=items.filter(x=>!x.acknowledged&&x.priority==='P1').length;
    panel.replaceChildren();
    const head=element('div','nexus-panel-head');head.append(element('strong','', 'Notificaciones inteligentes'),element('span','nexus-status',demo?'MODO DEMO':'CONECTADO A API'));panel.append(head);
    const filters=element('div','nexus-filters');[['all','Todas'],['urgent','Urgentes'],['pending','Pendientes']].forEach(([key,label])=>{const b=element('button','',label);b.type='button';b.setAttribute('aria-pressed',String(filter===key));b.addEventListener('click',()=>{filter=key;render();});filters.append(b);});panel.append(filters);
    const visible=items.filter(x=>filter==='all'||(filter==='urgent'&&x.priority==='P1')||(filter==='pending'&&!x.acknowledged));
    if(!visible.length)panel.append(element('p','nexus-empty','No hay avisos en esta categoría.'));
    for(const n of visible){const card=element('article','nexus-item');card.dataset.priority=n.priority;card.append(element('div','nexus-status',`${n.priority} · ${n.count||1} evento(s) · ${n.incident_id||'Sin incidente'}`),element('div','nexus-item-title',n.title),element('p','nexus-item-meta',n.description||''));const b=element('button','nexus-ack',n.acknowledged?'Reconocida':'Reconocer');b.type='button';b.disabled=!!n.acknowledged;b.addEventListener('click',()=>acknowledge(n.id));card.append(b);panel.append(card);}
  }
  bell.addEventListener('click',()=>{panel.hidden=!panel.hidden;bell.setAttribute('aria-expanded',String(!panel.hidden));});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){panel.hidden=true;bell.setAttribute('aria-expanded','false');}});
  load();if(!demo)setInterval(load,30000);
})();
