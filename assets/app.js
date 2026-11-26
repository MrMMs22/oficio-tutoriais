/* Ofício — interações (sem dependências) */
(function(){
  "use strict";
  var root=document.documentElement;
  var store={
    get:function(k,d){try{var v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch(e){return d}},
    set:function(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
  };
  function $(s,c){return (c||document).querySelector(s)}
  function $$(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))}
  function norm(s){return (s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"")}

  /* tema */
  var tbtn=$("[data-theme-toggle]");
  function syncThemeBtn(){
    if(!tbtn)return;
    var light=root.getAttribute("data-theme")==="light";
    tbtn.setAttribute("aria-label",light?"Ativar tema escuro":"Ativar tema claro");
    tbtn.setAttribute("title",light?"Tema escuro":"Tema claro");
    var m=$('meta[name="theme-color"]');if(m)m.setAttribute("content",light?"#f6f4ee":"#0b0c0a");
  }
  if(tbtn){
    tbtn.addEventListener("click",function(){
      var next=root.getAttribute("data-theme")==="light"?"dark":"light";
      root.setAttribute("data-theme",next);store.set("oficio:tema",next);syncThemeBtn();
    });
    syncThemeBtn();
  }

  /* cabeçalho com borda ao rolar */
  var top=$(".top");
  function onScroll(){if(top)top.classList.toggle("scrolled",window.scrollY>8)}
  window.addEventListener("scroll",onScroll,{passive:true});onScroll();

  /* toast */
  var toastEl;
  function toast(msg){
    if(!toastEl){toastEl=document.createElement("div");toastEl.className="toast";toastEl.setAttribute("role","status");document.body.appendChild(toastEl)}
    toastEl.textContent=msg;toastEl.classList.add("show");
    clearTimeout(toast._t);toast._t=setTimeout(function(){toastEl.classList.remove("show")},2200);
  }

  function doneCount(id){return (store.get("oficio:passos:"+id,[])||[]).length}

  /* ---------- página inicial ---------- */
  var list=$("#lista");
  if(list){
    var input=$("#q"),box=$(".searchbox"),countEl=$("[data-count]"),empty=$("[data-empty]"),sortSel=$("#ordem");
    var items=$$("li[data-cat]",list).map(function(li){
      return {el:li,cat:li.dataset.cat,min:+li.dataset.min,idx:+li.dataset.idx,title:li.dataset.title,text:norm(li.textContent+" "+(li.dataset.extra||"")),steps:+li.dataset.steps,id:li.dataset.id};
    });
    var state={q:"",cat:"todos",rapido:false,ordem:"padrao"};
    var p=new URLSearchParams(location.search);
    if(p.get("q"))state.q=p.get("q");
    if(["casa","jardim","eletronicos"].indexOf(p.get("cat"))>=0)state.cat=p.get("cat");
    if(p.get("rapido")==="1")state.rapido=true;
    if(["padrao","rapidos","az"].indexOf(p.get("ordem"))>=0)state.ordem=p.get("ordem");
    input.value=state.q;sortSel.value=state.ordem;

    // progresso salvo
    items.forEach(function(it){
      var n=doneCount(it.id);
      if(n>0){var f=$(".foot",it.el);var s=document.createElement("span");s.className="done";
        s.textContent=n>=it.steps?"✓ concluído":"● "+n+"/"+it.steps+" feitos";f.appendChild(s)}
    });

    function apply(push){
      var terms=norm(state.q).split(/\s+/).filter(Boolean);
      var vis=0;
      items.forEach(function(it){
        var ok=(state.cat==="todos"||it.cat===state.cat)&&(!state.rapido||it.min<=10)&&terms.every(function(t){return it.text.indexOf(t)>=0});
        it.el.hidden=!ok;if(ok)vis++;
      });
      var sorted=items.slice().sort(function(a,b){
        if(state.ordem==="rapidos")return a.min-b.min||a.idx-b.idx;
        if(state.ordem==="az")return a.title.localeCompare(b.title,"pt-BR");
        return a.idx-b.idx;
      });
      sorted.forEach(function(it){list.appendChild(it.el)});
      countEl.textContent=vis===1?"1 tutorial":vis+" tutoriais";
      empty.hidden=vis!==0;
      box.classList.toggle("has-q",!!state.q);
      $$("[data-filter]").forEach(function(b){b.setAttribute("aria-pressed",String(b.dataset.filter===state.cat))});
      $$("[data-cat-card]").forEach(function(b){b.setAttribute("aria-pressed",String(b.dataset.catCard===state.cat))});
      var rb=$("[data-rapido]");if(rb)rb.setAttribute("aria-pressed",String(state.rapido));
      if(push!==false){
        var u=new URLSearchParams();
        if(state.q)u.set("q",state.q);if(state.cat!=="todos")u.set("cat",state.cat);
        if(state.rapido)u.set("rapido","1");if(state.ordem!=="padrao")u.set("ordem",state.ordem);
        var qs=u.toString();
        history.replaceState(null,"",location.pathname+(qs?"?"+qs:"")+location.hash);
      }
    }
    var t;
    input.addEventListener("input",function(){clearTimeout(t);t=setTimeout(function(){state.q=input.value.trim();apply()},80)});
    $(".clear").addEventListener("click",function(){input.value="";state.q="";apply();input.focus()});
    $$("[data-filter]").forEach(function(b){b.addEventListener("click",function(){state.cat=b.dataset.filter;apply()})});
    $$("[data-cat-card]").forEach(function(b){b.addEventListener("click",function(){
      state.cat=state.cat===b.dataset.catCard?"todos":b.dataset.catCard;apply();
      $("#tutoriais").scrollIntoView({block:"start"});
    })});
    var rb=$("[data-rapido]");if(rb)rb.addEventListener("click",function(){state.rapido=!state.rapido;apply()});
    sortSel.addEventListener("change",function(){state.ordem=sortSel.value;apply()});
    $$("[data-reset]").forEach(function(b){b.addEventListener("click",function(){state={q:"",cat:"todos",rapido:false,ordem:"padrao"};input.value="";sortSel.value="padrao";apply();input.focus()})});
    document.addEventListener("keydown",function(e){
      if(e.key==="/"&&document.activeElement!==input&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();input.focus();input.select()}
      if(e.key==="Escape"&&document.activeElement===input&&input.value){input.value="";state.q="";apply()}
    });
    if(location.hash==="#busca"){input.focus()}
    apply(false);
  }

  /* ---------- página de tutorial ---------- */
  var art=$("article[data-id]");
  if(art){
    var id=art.dataset.id,steps=$$(".step",art),total=steps.length;
    var key="oficio:passos:"+id,mkey="oficio:material:"+id;
    var done=store.get(key,[])||[];
    var bar=$$(".progress i"),lbl=$$("[data-prog]"),fin=$(".finish");
    function render(){
      steps.forEach(function(s,i){
        var on=done.indexOf(i)>=0;s.classList.toggle("is-done",on);
        var b=$(".tick",s);b.setAttribute("aria-pressed",String(on));
        $(".tick-txt",s).textContent=on?"Feito":"Marcar";
      });
      var pct=total?Math.round(done.length/total*100):0;
      bar.forEach(function(b){b.style.width=pct+"%"});
      lbl.forEach(function(l){l.textContent=done.length+" de "+total+" passos"});
      if(fin)fin.classList.toggle("show",done.length===total&&total>0);
    }
    steps.forEach(function(s,i){
      $(".tick",s).addEventListener("click",function(){
        var k=done.indexOf(i);if(k>=0)done.splice(k,1);else done.push(i);
        store.set(key,done);render();
        if(done.length===total)toast("Pronto! Tudo feito 🎉");
      });
    });
    $$("[data-reset-steps]").forEach(function(b){b.addEventListener("click",function(){done=[];store.set(key,done);store.set(mkey,[]);
      $$(".checklist input",art).forEach(function(c){c.checked=false});render();toast("Progresso zerado")})});
    var mat=store.get(mkey,[])||[];
    $$(".checklist input",art).forEach(function(c,i){
      c.checked=mat.indexOf(i)>=0;
      c.addEventListener("change",function(){
        var k=mat.indexOf(i);if(c.checked&&k<0)mat.push(i);if(!c.checked&&k>=0)mat.splice(k,1);store.set(mkey,mat);
      });
    });
    render();

    var share=$("[data-share]");
    if(share)share.addEventListener("click",function(){
      var data={title:document.title,url:location.href.split("#")[0]};
      if(navigator.share){navigator.share(data).catch(function(){})}
      else if(navigator.clipboard){navigator.clipboard.writeText(data.url).then(function(){toast("Link copiado")},function(){toast(data.url)})}
      else toast(data.url);
    });
    var pr=$("[data-print]");if(pr)pr.addEventListener("click",function(){window.print()});

    // sumário ativo
    var links=$$(".toc a");
    if(links.length&&"IntersectionObserver" in window){
      var map={};links.forEach(function(a){map[a.getAttribute("href").slice(1)]=a});
      var io=new IntersectionObserver(function(es){
        es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.remove("active")});var a=map[e.target.id];if(a)a.classList.add("active")}});
      },{rootMargin:"-30% 0px -60% 0px"});
      Object.keys(map).forEach(function(k){var el=document.getElementById(k);if(el)io.observe(el)});
    }
    document.addEventListener("keydown",function(e){
      if(/input|textarea|select/i.test(document.activeElement.tagName)||e.metaKey||e.ctrlKey||e.altKey)return;
      var a;
      if(e.key==="ArrowLeft")a=$(".pager .prev");
      if(e.key==="ArrowRight")a=$(".pager .next");
      if(a)location.href=a.href;
    });
  }
})();

/* ---------- efeitos ---------- */
(function(){
  "use strict";
  var reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine=matchMedia("(hover: hover) and (pointer: fine)").matches;
  var root=document.documentElement;

  // barra de leitura
  var rb=document.querySelector(".readbar i");
  function read(){var h=document.documentElement.scrollHeight-innerHeight;root.style.setProperty("--read",h>0?Math.min(1,scrollY/h):0)}
  if(rb){addEventListener("scroll",read,{passive:true});addEventListener("resize",read);read()}

  // ripple nos botões
  document.addEventListener("pointerdown",function(e){
    if(reduce)return;
    var b=e.target.closest(".btn,.chip,.iconbtn,.tick");if(!b)return;
    var r=b.getBoundingClientRect(),s=Math.max(r.width,r.height),d=document.createElement("span");
    d.className="ripple";d.style.cssText="width:"+s+"px;height:"+s+"px;left:"+(e.clientX-r.left-s/2)+"px;top:"+(e.clientY-r.top-s/2)+"px";
    b.appendChild(d);setTimeout(function(){d.remove()},650);
  });

  if(reduce)return;
  root.classList.add("fx");

  // revelar ao rolar
  var els=document.querySelectorAll(".card,.cat,.stat,.sec,.callout,.pager a,.about>div,.panel,.related>h2");
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add("in");io.unobserve(en.target)}})},{rootMargin:"0px 0px -6% 0px"});
    var row=0,lastTop=null;
    Array.prototype.forEach.call(els,function(el){
      var t=el.getBoundingClientRect().top;if(t!==lastTop){row=0;lastTop=t}else row++;
      el.style.setProperty("--d",Math.min(row,4)*70+"ms");
      el.classList.add("rv");io.observe(el);
    });
    // itens que reaparecem após filtro já devem estar visíveis
    var list=document.getElementById("lista");
    if(list)new MutationObserver(function(){Array.prototype.forEach.call(list.querySelectorAll(".card"),function(c){c.classList.add("in")})}).observe(list,{childList:true,subtree:true,attributes:true,attributeFilter:["hidden"]});
  }

  // tilt 3D + brilho seguindo o mouse
  if(fine){
    document.addEventListener("pointermove",function(e){
      var c=e.target.closest(".card,.cat");if(!c)return;
      var r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
      c.style.setProperty("--mx",x*100+"%");c.style.setProperty("--my",y*100+"%");
      if(c.classList.contains("card")){c.style.setProperty("--rx",((.5-y)*8).toFixed(2)+"deg");c.style.setProperty("--ry",((x-.5)*10).toFixed(2)+"deg")}
    },{passive:true});
    document.addEventListener("pointerout",function(e){
      var c=e.target.closest(".card");if(c&&!c.contains(e.relatedTarget)){c.style.setProperty("--rx","0deg");c.style.setProperty("--ry","0deg")}
    });
  }

  // contadores animados
  Array.prototype.forEach.call(document.querySelectorAll(".stat strong"),function(el){
    var m=el.textContent.match(/^(\D*)(\d+)$/);if(!m)return;var end=+m[2],t0=null;
    function step(t){if(!t0)t0=t;var p=Math.min(1,(t-t0)/1100),v=Math.round(end*(1-Math.pow(1-p,3)));el.textContent=m[1]+v;if(p<1)requestAnimationFrame(step)}
    el.textContent=m[1]+"0";requestAnimationFrame(step);
  });

  // confete quando termina todos os passos
  var fin=document.querySelector(".finish");
  if(fin)new MutationObserver(function(){
    if(!fin.classList.contains("show"))return;
    var cols=["#d8ff3c","#7ee0c6","#ff6a3d","#ffb020","#f4f1ea"];
    for(var i=0;i<70;i++)(function(){
      var d=document.createElement("i");d.className="confetti";d.style.background=cols[i%5];document.body.appendChild(d);
      var x=innerWidth/2,y=innerHeight*.6,a=Math.random()*Math.PI-Math.PI,v=6+Math.random()*9,vx=Math.cos(a)*v,vy=Math.sin(a)*v-4,r=0,vr=(Math.random()-.5)*20,n=0;
      (function f(){n++;vy+=.32;vx*=.99;x+=vx;y+=vy;r+=vr;d.style.transform="translate("+x+"px,"+y+"px) rotate("+r+"deg)";d.style.opacity=Math.max(0,1-n/110);
        if(n<110)requestAnimationFrame(f);else d.remove()})();
    })();
  }).observe(fin,{attributes:true,attributeFilter:["class"]});

  // partículas conectadas no fundo (leve: pausa fora da aba, poucas no celular)
  var cv=document.getElementById("fx-particles");
  if(cv&&cv.getContext){
    var ctx=cv.getContext("2d"),dpr=Math.min(2,devicePixelRatio||1),W,H,P=[],mouse={x:-999,y:-999},run=true;
    function size(){W=cv.clientWidth;H=cv.clientHeight;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
      var n=Math.round(Math.min(70,W*H/22000));P=[];for(var i=0;i<n;i++)P.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35,r:Math.random()*1.6+.6})}
    size();addEventListener("resize",size);
    addEventListener("pointermove",function(e){mouse.x=e.clientX;mouse.y=e.clientY},{passive:true});
    document.addEventListener("visibilitychange",function(){run=!document.hidden;if(run)requestAnimationFrame(draw)});
    function draw(){
      if(!run)return;
      var light=root.getAttribute("data-theme")==="light",col=light?"74,100,0":"216,255,60";
      ctx.clearRect(0,0,W,H);
      for(var i=0;i<P.length;i++){var p=P[i];p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;
        var dx=p.x-mouse.x,dy=p.y-mouse.y,dm=dx*dx+dy*dy;if(dm<14400){p.x+=dx*.012;p.y+=dy*.012}
        ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.283);ctx.fillStyle="rgba("+col+",.55)";ctx.fill();
        for(var j=i+1;j<P.length;j++){var q=P[j],ex=p.x-q.x,ey=p.y-q.y,d2=ex*ex+ey*ey;if(d2<13000){ctx.strokeStyle="rgba("+col+","+(0.16*(1-d2/13000))+")";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}}}
      requestAnimationFrame(draw);
    }
    requestAnimationFrame(draw);
  }
})();

/* ---------- monetização (config em assets/config.js) ---------- */
(function(){
  "use strict";
  var C=window.OFICIO_CONFIG||{};
  var bmc=(C.BMC_URL||"").trim();
  if(/^https:\/\//.test(bmc)){
    Array.prototype.forEach.call(document.querySelectorAll("[data-bmc]"),function(a){a.href=bmc;a.hidden=false});
    Array.prototype.forEach.call(document.querySelectorAll("[data-bmc-box]"),function(b){b.hidden=false});
  }
  var client=(C.ADSENSE_CLIENT||"").trim(),slots=C.ADSENSE_SLOTS||{};
  if(!/^ca-pub-\d+$/.test(client))return;
  var used=[];
  Array.prototype.forEach.call(document.querySelectorAll("[data-ad]"),function(box){
    var id=(slots[box.dataset.ad]||"").trim();if(!/^\d+$/.test(id))return;
    var ins=document.createElement("ins");ins.className="adsbygoogle";ins.style.display="block";
    ins.setAttribute("data-ad-client",client);ins.setAttribute("data-ad-slot",id);
    ins.setAttribute("data-ad-format","auto");ins.setAttribute("data-full-width-responsive","true");
    box.appendChild(ins);box.hidden=false;used.push(ins);
  });
  if(!used.length)return;
  var s=document.createElement("script");s.async=true;s.crossOrigin="anonymous";
  s.src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client="+encodeURIComponent(client);
  document.head.appendChild(s);
  used.forEach(function(){(window.adsbygoogle=window.adsbygoogle||[]).push({})});
})();
