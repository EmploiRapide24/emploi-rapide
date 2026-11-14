// Emploi Rapide 24 : fonctionne hors connexion avec la dernière liste téléchargée
const C='emploi-rapide-v51';
const SHELL=['./','index.html','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png','confidentialite.html'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim();});
self.addEventListener('push',e=>{let d={};try{d=e.data.json()}catch(x){d={title:'Emploi Rapide 24',body:e.data?e.data.text():''}}
  e.waitUntil(self.registration.showNotification(d.title||'Nouvelles offres d'emploi',{body:d.body||'',icon:'icons/icon-192.png',badge:'icons/icon-192.png',data:{url:d.url||'/'},tag:'er24-offres',renotify:true}));});
self.addEventListener('notificationclick',e=>{e.notification.close();const u=(e.notification.data&&e.notification.data.url)||'/';
  e.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(l=>{for(const c of l){if('focus' in c){c.navigate(u);return c.focus();}}return clients.openWindow(u);}));});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin) return;
  // Réseau d'abord (offres fraîches), cache en secours (hors connexion)
  e.respondWith(fetch(e.request,{cache:'no-cache'}).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r;})
    .catch(()=>caches.match(e.request).then(r=>r||caches.match('index.html'))));
});
