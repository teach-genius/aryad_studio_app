(function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H;
  let nodes = [];
  const mouse = { x: -9999, y: -9999 };

  function resize() {
  const w = canvas.offsetWidth;
  const h = canvas.offsetHeight;
  W = canvas.width  = w;
  H = canvas.height = h;
}
  function createNodes(count) {
    nodes = [];
    for (let i = 0; i < count; i++) {
      nodes.push({
        x:     Math.random() * W,
        y:     Math.random() * H,
        vx:    (Math.random() - 0.5) * 0.3,
        vy:    (Math.random() - 0.5) * 0.3,
        r:     Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.4 + 0.1,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    const isDark    = document.documentElement.getAttribute('data-theme') !== 'light';
    const nodeColor = isDark ? '180,200,255' : '79,127,255';
    const lineColor = isDark ? '100,140,255' : '79,127,255';

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx   = nodes[i].x - nodes[j].x;
        const dy   = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(${lineColor},${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth   = 0.5;
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.stroke();
        }
      }
    }

    nodes.forEach(n => {
      const dx   = n.x - mouse.x;
      const dy   = n.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 160) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(79,127,255,${0.2 * (1 - dist / 160)})`;
        ctx.lineWidth   = 0.8;
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
      }
    });

    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${nodeColor},${n.alpha})`;
      ctx.fill();

      n.x += n.vx;
      n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });

    requestAnimationFrame(draw);
  }

  const hero = document.getElementById('hero');
  if (hero) {
    hero.addEventListener('mousemove', e => {
      const rect = hero.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });
    hero.addEventListener('mouseleave', () => {
      mouse.x = -9999;
      mouse.y = -9999;
    });
  }

  window.addEventListener('resize', () => {
    resize();
    createNodes(60);
  }, { passive: true });

  resize();
  createNodes(60);
  draw();
})();


(function initReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();


(function initThemeToggle() {
  const btn  = document.getElementById('themeToggle');
  const html = document.documentElement;
  const nav  = document.getElementById('navbar');

  if (!btn) return;

  const SVG_MOON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-moon"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 1.992a10 10 0 1 0 9.236 13.838c.341 -.82 -.476 -1.644 -1.298 -1.31a6.5 6.5 0 0 1 -6.864 -10.787l.077 -.08c.551 -.63 .113 -1.653 -.758 -1.653h-.266l-.068 -.006l-.06 -.002z" /></svg>`;
  const SVG_SUN  = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-brightness-down"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 8a4 4 0 1 1 -3.995 4.2l-.005 -.2l.005 -.2a4 4 0 0 1 3.995 -3.8z" /><path d="M12 4a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M19 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M12 18a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M5 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /></svg>`;

  const saved = localStorage.getItem('aryad-theme');
  if (saved) {
    html.setAttribute('data-theme', saved);
    btn.innerHTML = saved === 'dark' ? SVG_MOON : SVG_SUN;
  }

  btn.addEventListener('click', () => {
    const isDark   = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    btn.innerHTML = isDark ? SVG_SUN : SVG_MOON;
    localStorage.setItem('aryad-theme', newTheme);

    if (nav) {
      nav.style.background = isDark
        ? 'rgba(245,245,247,0.8)'
        : 'rgba(6,7,10,0.7)';
    }
  });
})();


(function initMobileMenu() {
  const hamburger  = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (!hamburger || !mobileMenu) return;

  let isOpen = false;

  function openMenu() {
    isOpen = true;
    mobileMenu.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    hamburger.children[0].style.transform = 'rotate(45deg) translate(4px,4px)';
    hamburger.children[1].style.opacity   = '0';
    hamburger.children[2].style.transform = 'rotate(-45deg) translate(4px,-4px)';
  }

  function closeMenu() {
    isOpen = false;
    mobileMenu.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.children[0].style.transform = '';
    hamburger.children[1].style.opacity   = '';
    hamburger.children[2].style.transform = '';
  }

  hamburger.addEventListener('click', () => isOpen ? closeMenu() : openMenu());

  window.closeMobile = closeMenu;

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && isOpen) closeMenu();
  });
})();


window.filterTech = function filterTech(cat, clickedBtn) {
  document.querySelectorAll('.tech-cat-btn').forEach(btn => {
    btn.classList.remove('active');
    btn.setAttribute('aria-pressed', 'false');
  });

  if (clickedBtn) {
    clickedBtn.classList.add('active');
    clickedBtn.setAttribute('aria-pressed', 'true');
  }

  document.querySelectorAll('.tech-item').forEach(item => {
    const show = (cat === 'all' || item.dataset.cat === cat);
    item.style.display = show ? '' : 'none';
  });
};


(function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  // offsetTop mis en cache — évite le reflow forcé dans le scroll handler
  let sectionTops = [];
  function cacheSections() {
    sectionTops = Array.from(sections).map(s => ({
      id:  s.id,
      top: s.offsetTop,
    }));
  }
  cacheSections();
  window.addEventListener('resize', cacheSections, { passive: true });

  window.addEventListener('scroll', () => {
    let current = '';
    sectionTops.forEach(s => {
      if (window.scrollY >= s.top - 90) current = s.id;
    });
    navLinks.forEach(a => {
      const href = a.getAttribute('href') || '';
      a.style.color = href.includes('#' + current) ? 'var(--text-primary)' : '';
    });
  }, { passive: true });
})();


(function initScrollTop() {
  const btn = document.getElementById('scrollTop');
  if (!btn) return;

  // Bouton "retour en haut" visible après 300px de scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();