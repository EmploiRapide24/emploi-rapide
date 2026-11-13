/* Mesure d'audience des pages statiques (même consentement que l'accueil) */
(function(){var ID='G-Y7XXSVJCYY',K='er-ga';
function get(){try{return localStorage.getItem(K)}catch(e){return null}}
function set(v){try{localStorage.setItem(K,v)}catch(e){}}
function load(){if(window.__ga)return;window.__ga=1;var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',ID,{anonymize_ip:true});}
function T(n,p){try{if(window.gtag)gtag('event',n,p||{})}catch(e){}}
function banner(){var b=document.createElement('div');b.style.cssText='position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:560px;margin:0 auto;background:#0f1a33;color:#fff;border-radius:14px;padding:14px 16px;font:14px/1.45 system-ui,sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.25)';
b.innerHTML='<div>Nous utilisons Google Analytics (cookies de mesure d\'audience) pour compter les visites. Aucune publicité ciblée. <a href="/confidentialite.html" style="color:#fcd34d">En savoir plus</a></div><div style="display:flex;gap:8px;margin-top:10px;justify-content:flex-end"><button style="background:transparent;color:#fff;border:1px solid #fff6;border-radius:999px;padding:8px 14px;font:inherit;cursor:pointer">Refuser</button><button style="background:#f5b800;color:#0f1a33;border:0;border-radius:999px;padding:8px 16px;font:inherit;font-weight:800;cursor:pointer">Accepter</button></div>';
document.body.appendChild(b);var bt=b.querySelectorAll('button');bt[0].onclick=function(){set('0');b.remove()};bt[1].onclick=function(){set('1');b.remove();load()};}
var v=get();if(v==='1')load();else if(v!=='0')setTimeout(banner,1200);
document.addEventListener('click',function(e){var a=e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
 if(/wa\.me/.test(h))T('partage_whatsapp',{page:location.pathname});
 else if(a.classList.contains('g'))T('clic_postuler',{page:location.pathname});
 else if(/#alerte/.test(h))T('clic_alerte',{page:location.pathname});},true);
})();
