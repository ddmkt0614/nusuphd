/* 누수박사 움직임 — clay.com 인터랙션을 GSAP 3.15 로 옮김.
   clay app.js 에서 확인한 값: 글자 마스크 상승(stagger .02), 묶음 등장(y24 · .6s · power3.out · stagger .08),
   화살표 바꿔치기(.4s · clayRegular), 쌓이는 카드(scale .85), 커서 말풍선(back.out(1.7)), 숫자 카운터, Flip.
   내용은 HTML 에 최종 모습으로 있고, 여기서는 움직임만 더한다. 동작 줄이기 설정이면 아무것도 하지 않는다. */
(function () {
  var root = document.documentElement;
  function release() { root.classList.remove("motion-on"); }
  /* 동작 줄이기면 첫 화면 영상도 멈추고 첫 장면(포스터)만 */
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    Array.prototype.forEach.call(document.querySelectorAll(".hero-video"), function (v) { v.removeAttribute("autoplay"); v.pause(); });
  }
  if (!window.gsap || matchMedia("(prefers-reduced-motion: reduce)").matches) { release(); return; }
  window.__motion = true;

  var gsap = window.gsap;
  gsap.registerPlugin(ScrollTrigger, SplitText, Flip, CustomEase);
  CustomEase.create("clayRegular", "M0,0 C0.625,0.05 0,1 1,1");
  CustomEase.create("claySmooth", "M0,0 C0.38,0.005 0.215,1 1,1");
  var $ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var fine = matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* 1. 머리: 내리면 숨고 올리면 나타남, 스크롤 뒤 밑줄 */
  var header = document.querySelector(".site-header");
  if (header) {
    root.style.setProperty("--hd", header.offsetHeight + "px");
    ScrollTrigger.create({
      start: 0, end: "max",
      onUpdate: function (self) {
        var y = self.scroll();
        header.classList.toggle("is-scrolled", y > 8);
        header.classList.toggle("is-hidden", self.direction === 1 && y > 240);
      }
    });
  }

  /* 2. 글자 마스크 상승: 첫 화면 h1 은 바로, 나머지 큰 제목은 화면에 들어올 때 */
  function splitRise(el, delay, onView) {
    var split = new SplitText(el, { type: "lines,chars", linesClass: "split-mask" });
    gsap.set(el, { visibility: "visible" });
    var tween = gsap.from(split.chars, {
      yPercent: 110, duration: 0.9, ease: "clayRegular", stagger: 0.02, delay: delay || 0,
      paused: !!onView, onComplete: function () { split.revert(); }
    });
    if (onView) ScrollTrigger.create({ trigger: el, start: "top 88%", once: true, onEnter: function () { tween.play(); } });
  }

  /* 글꼴이 늦으면 1.2초 뒤 그냥 시작(첫 화면이 오래 숨지 않게) */
  Promise.race([document.fonts.ready, new Promise(function (r) { setTimeout(r, 1200); })]).then(function () {
    var h1 = document.querySelector(".hero h1");
    if (h1) splitRise(h1, 0.05);
    var rest = $(".hero-copy > :not(h1)");
    gsap.fromTo(rest, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out", stagger: 0.08, delay: 0.35 });
    var vis = document.querySelector(".hero-visual");
    if (vis) gsap.fromTo(vis, { autoAlpha: 0, y: 40, scale: 0.96 }, { autoAlpha: 1, y: 0, scale: 1, duration: 1.1, ease: "claySmooth", delay: 0.3 });
    release();
    $(".block-title, .finder-head h2, .callout h2, .ins-band h2, .block h1").forEach(function (el) { splitRise(el, 0, true); });
    ScrollTrigger.refresh();
  });

  /* 3. 묶음 등장 (clay data-visibility: y24 · .6s · power3.out · stagger .08) */
  var groups = ".svc-item, .place-card, .trust li, .faq details, .facts > div, .case-item, .signs li, .hub, .summary .wrap > *, .lead, .split-media, .ins-docs, .callout p, .finder-box, .finder-tabs";
  gsap.set(groups, { autoAlpha: 0, y: 24 });
  ScrollTrigger.batch(groups, {
    start: "top 90%", once: true,
    onEnter: function (els) { gsap.to(els, { autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out", stagger: 0.08, overwrite: true }); }
  });
  /* 지역 카드는 수가 많아 앞쪽만 차례로 */
  $(".region-grid").forEach(function (grid) {
    var items = $("a", grid).slice(0, 30);
    gsap.set(items, { autoAlpha: 0, y: 16 });
    ScrollTrigger.create({ trigger: grid, start: "top 92%", once: true,
      onEnter: function () { gsap.to(items, { autoAlpha: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.02 }); } });
  });

  /* 4. 사진: 테두리 안에서 살짝 확대가 풀리며 스크롤 따라 움직임 */
  $(".wide-img, .split-media img").forEach(function (img) {
    var box = document.createElement("div");
    box.className = "media-clip";
    img.parentNode.insertBefore(box, img); box.appendChild(img);
    gsap.fromTo(img, { scale: 1.12, yPercent: -4 }, { scale: 1, yPercent: 4, ease: "none",
      scrollTrigger: { trigger: box, start: "top bottom", end: "bottom top", scrub: true } });
  });
  $(".svc-img").forEach(function (img) {
    gsap.fromTo(img, { scale: 1.08 }, { scale: 1, ease: "none", scrollTrigger: { trigger: img, start: "top bottom", end: "bottom 60%", scrub: true } });
  });

  /* 5. 화살표 바꿔치기 (clay data-hover-arrow) */
  function addArrow(host, holder) {
    var a = document.createElement("span");
    a.className = "arw"; a.setAttribute("aria-hidden", "true");
    a.innerHTML = "<i>↗</i><i>↗</i>";
    (holder || host).appendChild(a);
    var it = a.children;
    gsap.set(it[1], { xPercent: -100, yPercent: 100 });
    if (!fine) return;
    host.addEventListener("mouseenter", function () {
      gsap.to(it[0], { xPercent: 100, yPercent: -100, duration: 0.4, ease: "clayRegular", overwrite: "auto" });
      gsap.to(it[1], { xPercent: 0, yPercent: 0, duration: 0.4, ease: "clayRegular", overwrite: "auto" });
    });
    host.addEventListener("mouseleave", function () {
      gsap.to(it[0], { xPercent: 0, yPercent: 0, duration: 0.4, ease: "clayRegular", overwrite: "auto" });
      gsap.to(it[1], { xPercent: -100, yPercent: 100, duration: 0.4, ease: "clayRegular", overwrite: "auto" });
    });
  }
  $(".svc-item a").forEach(function (a) { addArrow(a, a.querySelector(".svc-text strong")); });
  $(".btn-line, .more-link a").forEach(function (a) { addArrow(a); });

  /* 6. 커서 따라다니는 말풍선 (clay logo-cursor: back.out(1.7)) — 마우스 있는 화면만 */
  if (fine) {
    var tip = document.createElement("div");
    tip.className = "cursor-tip"; tip.setAttribute("aria-hidden", "true");
    document.body.appendChild(tip);
    var tx = gsap.quickTo(tip, "x", { duration: 0.45, ease: "power3" });
    var ty = gsap.quickTo(tip, "y", { duration: 0.45, ease: "power3" });
    var on = false;
    document.addEventListener("mousemove", function (e) { tx(e.clientX + 16); ty(e.clientY + 18); });
    $(".svc-item a, .region-grid a, .place-card").forEach(function (el) {
      var label = el.classList.contains("place-card") ? "네이버 플레이스 열기" : el.closest(".region-grid") ? "출장 안내 보기" : "자세히 보기";
      el.addEventListener("mouseenter", function (e) {
        tip.textContent = label;
        if (!on) { gsap.set(tip, { x: e.clientX + 16, y: e.clientY + 18 }); on = true; }
        gsap.to(tip, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)", overwrite: "auto" });
      });
      el.addEventListener("mouseleave", function () {
        on = false;
        gsap.to(tip, { autoAlpha: 0, scale: 0.8, duration: 0.2, ease: "power2.in", overwrite: "auto" });
      });
    });
  }

  /* 7. 쌓이는 카드 (clay data-stack-card: 뒤 카드가 .85 까지 작아지며 겹침) */
  $(".steps").forEach(function (list) {
    var cards = $("li", list);
    if (cards.length < 3) return;
    list.classList.add("is-stack");
    cards.forEach(function (card, i) {
      card.style.setProperty("--i", i);
      var next = cards[i + 1];
      if (!next) return;
      gsap.fromTo(card, { scale: 1, filter: "brightness(1)" }, { scale: 0.85 + i * 0.025, filter: "brightness(0.93)", ease: "none",
        scrollTrigger: { trigger: next, start: "top bottom", end: "top " + (header ? header.offsetHeight + 40 : 140) + "px", scrub: true } });
    });
  });

  /* 8. 숫자 카운터 (한 번만, 글자 폭 고정) */
  $(".hero-area span, .hero-area b, .region-grid span").slice(0, 120).forEach(function (el) {
    var node = el.firstChild;
    if (!node || node.nodeType !== 3 || !/\d/.test(node.nodeValue)) return;
    var text = node.nodeValue, nums = text.match(/\d+/g).map(Number), obj = { p: 0 };
    el.setAttribute("aria-label", el.textContent);
    el.style.fontVariantNumeric = "tabular-nums";
    function draw() { var k = 0; node.nodeValue = text.replace(/\d+/g, function () { return Math.round(nums[k++] * obj.p); }); }
    draw();
    ScrollTrigger.create({ trigger: el, start: "top 95%", once: true,
      onEnter: function () { gsap.to(obj, { p: 1, duration: 1.2, ease: "claySmooth", onUpdate: draw }); } });
  });

  /* 9. 지역 탭: 검정 알약이 Flip 으로 미끄러지고 새 카드가 차례로 */
  $(".finder-tabs").forEach(function (tabs) {
    var pill = document.createElement("span");
    pill.className = "finder-pill"; pill.setAttribute("aria-hidden", "true");
    tabs.appendChild(pill); tabs.classList.add("has-pill");
    function place(active) {
      pill.style.left = active.offsetLeft + "px"; pill.style.top = active.offsetTop + "px";
      pill.style.width = active.offsetWidth + "px"; pill.style.height = active.offsetHeight + "px";
    }
    var cur = tabs.querySelector('[aria-pressed="true"]');
    if (cur) place(cur);
    /* 웹 글꼴이 늦게 오면 탭 폭이 바뀌므로 글꼴 로드 뒤·창 크기 변화 때 다시 맞춤 */
    function replace() { var a = tabs.querySelector('[aria-pressed="true"]'); if (a) place(a); }
    if (document.fonts) document.fonts.ready.then(replace);
    addEventListener("load", replace);
    if (window.ResizeObserver) { var ro = new ResizeObserver(replace); $(".finder-tab", tabs).forEach(function (t) { ro.observe(t); }); }
    addEventListener("resize", function () { var a = tabs.querySelector('[aria-pressed="true"]'); if (a) place(a); });
    $(".finder-tab", tabs).forEach(function (b) {
      b.addEventListener("click", function () {
        var state = Flip.getState(pill);
        place(b);
        Flip.from(state, { duration: 0.5, ease: "clayRegular" });
        setTimeout(function () {
          var panel = document.querySelector('.region-grid[data-panel="' + b.getAttribute("data-tab") + '"]');
          if (panel) gsap.fromTo($("a", panel).slice(0, 40), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: "power3.out", stagger: 0.015, overwrite: true });
        }, 0);
      });
    });
  });

  /* 10. 지역명 흐르는 띠 (clay 고객 로고 marquee) — 첫 화면 아래, 스크롤 방향 따라 속도·방향 바뀜 */
  var hero = document.querySelector(".page-home .hero");
  var names = [];
  $('.region-grid[data-panel="seoul"] strong, .region-grid[data-panel="gyeonggi"] strong').forEach(function (s) {
    var n = s.textContent.split(" ")[1]; if (n && names.indexOf(n) < 0) names.push(n);
  });
  if (hero && names.length >= 8) {  /* 공개 지역이 적을 땐 띠를 띄우지 않음 */
    var band = document.createElement("div");
    band.className = "marquee"; band.setAttribute("aria-hidden", "true");
    var track = document.createElement("div");
    track.className = "marquee-track";
    names.concat(names).forEach(function (n) { var sp = document.createElement("span"); sp.textContent = n; track.appendChild(sp); });
    band.appendChild(track);
    hero.insertAdjacentElement("afterend", band);
    var loop = gsap.to(track, { xPercent: -50, duration: names.length * 1.6, ease: "none", repeat: -1 });
    ScrollTrigger.create({ trigger: band, start: "top bottom", end: "bottom top",
      onUpdate: function (self) {
        gsap.to(loop, { timeScale: self.direction * Math.min(4, 1 + Math.abs(self.getVelocity()) / 600), duration: 0.3, overwrite: true });
        gsap.to(loop, { timeScale: self.direction, duration: 0.8, delay: 0.3, overwrite: false });
      } });
    if (fine) {
      band.addEventListener("mouseenter", function () { gsap.to(loop, { timeScale: 0.2, duration: 0.5 }); });
      band.addEventListener("mouseleave", function () { gsap.to(loop, { timeScale: 1, duration: 0.5 }); });
    }
  }

  /* 11. 자주 묻는 질문: 열고 닫을 때 높이를 부드럽게 */
  $(".faq details").forEach(function (d) {
    var s = d.querySelector("summary"), p = d.querySelector("p");
    if (!s || !p) return;
    s.addEventListener("click", function (e) {
      e.preventDefault();
      if (d.open) {
        gsap.to(p, { height: 0, autoAlpha: 0, duration: 0.35, ease: "power2.in", onComplete: function () { d.open = false; gsap.set(p, { clearProps: "all" }); } });
      } else {
        d.open = true;
        gsap.fromTo(p, { height: 0, autoAlpha: 0 }, { height: "auto", autoAlpha: 1, duration: 0.5, ease: "clayRegular", clearProps: "height" });
      }
    });
  });

  /* 12. 연락 버튼: 누를 때 살짝 눌림 + 자석처럼 커서 따라감 */
  if (fine) {
    $(".btn-call").forEach(function (b) {
      var mx = gsap.quickTo(b, "x", { duration: 0.5, ease: "power3" }), my = gsap.quickTo(b, "y", { duration: 0.5, ease: "power3" });
      b.addEventListener("mousemove", function (e) { var r = b.getBoundingClientRect(); mx((e.clientX - r.left - r.width / 2) * 0.18); my((e.clientY - r.top - r.height / 2) * 0.25); });
      b.addEventListener("mouseleave", function () { mx(0); my(0); });
    });
  }
})();
