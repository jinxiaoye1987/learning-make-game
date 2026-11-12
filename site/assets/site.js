(function(){
  var root=document.documentElement;
  var saved=localStorage.getItem('cg-theme'); if(saved) root.dataset.theme=saved;
  function isDark(){return root.dataset.theme? root.dataset.theme==='dark' : matchMedia('(prefers-color-scheme: dark)').matches;}
  window.CG={isDark:isDark};
  document.addEventListener('DOMContentLoaded',function(){
    var b=document.getElementById('themeBtn');
    if(b){b.textContent=isDark()?'☀ 浅色':'☾ 深色';
      b.onclick=function(){root.dataset.theme=isDark()?'light':'dark';localStorage.setItem('cg-theme',root.dataset.theme);location.reload();};}
    // lightbox
    var lb=document.getElementById('lightbox');
    if(lb){var lbi=lb.querySelector('img');
      document.querySelectorAll('figure img').forEach(function(i){i.addEventListener('click',function(){lbi.src=i.src;lb.style.display='flex';});});
      lb.addEventListener('click',function(){lb.style.display='none';});}
    // toc highlight
    var links=[].slice.call(document.querySelectorAll('nav.toc a'));
    if(links.length&&'IntersectionObserver' in window){
      var obs=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id);});}});},{rootMargin:'-20% 0px -70% 0px'});
      document.querySelectorAll('main section[id]').forEach(function(s){obs.observe(s);});}
    // mermaid
    if(window.mermaid&&document.querySelector('.mermaid')){
      mermaid.initialize({startOnLoad:false,theme:isDark()?'dark':'default',securityLevel:'loose',flowchart:{htmlLabels:true}});
      mermaid.run({querySelector:'.mermaid'}).then(function(){document.body.dataset.mermaid='done';}).catch(function(e){console.error(e);document.body.dataset.mermaid='error';});
    } else document.body.dataset.mermaid='none';
  });
})();
document.querySelectorAll('pre').forEach(function(p){var b=document.createElement('button');b.className='cp';b.type='button';b.textContent='复制';b.onclick=function(){var t=p.querySelector('code')?p.querySelector('code').innerText:p.innerText;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent='已复制';setTimeout(function(){b.textContent='复制'},1200)}).catch(function(){var r=document.createRange();r.selectNodeContents(p);var s=getSelection();s.removeAllRanges();s.addRange(r);});};p.appendChild(b);});
