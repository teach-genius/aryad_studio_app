(function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H;
  let nodes = [];
  const mouse = { x: -9999, y: -9999 };

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
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

    const isDark     = document.documentElement.getAttribute('data-theme') !== 'light';
    const nodeColor  = isDark ? '180,200,255' : '79,127,255';
    const lineColor  = isDark ? '100,140,255' : '79,127,255';

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
  });

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

  const saved = localStorage.getItem('aryad-theme');
  if (saved) {
    html.setAttribute('data-theme', saved);
    btn.innerHTML = saved === 'dark' ? `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-moon"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 1.992a10 10 0 1 0 9.236 13.838c.341 -.82 -.476 -1.644 -1.298 -1.31a6.5 6.5 0 0 1 -6.864 -10.787l.077 -.08c.551 -.63 .113 -1.653 -.758 -1.653h-.266l-.068 -.006l-.06 -.002z" /></svg>
    ` : `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-brightness-down"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 8a4 4 0 1 1 -3.995 4.2l-.005 -.2l.005 -.2a4 4 0 0 1 3.995 -3.8z" /><path d="M12 4a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M19 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M12 18a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M5 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /></svg>`;
  }

  btn.addEventListener('click', () => {
    const isDark  = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    btn.innerHTML = isDark ? `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-brightness-down"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 8a4 4 0 1 1 -3.995 4.2l-.005 -.2l.005 -.2a4 4 0 0 1 3.995 -3.8z" /><path d="M12 4a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M19 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M17 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M12 18a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 16a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M5 11a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /><path d="M7 6a1 1 0 0 1 .993 .883l.007 .127a1 1 0 0 1 -1.993 .117l-.007 -.127a1 1 0 0 1 1 -1z" /></svg>` : `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-moon"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 1.992a10 10 0 1 0 9.236 13.838c.341 -.82 -.476 -1.644 -1.298 -1.31a6.5 6.5 0 0 1 -6.864 -10.787l.077 -.08c.551 -.63 .113 -1.653 -.758 -1.653h-.266l-.068 -.006l-.06 -.002z" /></svg>
    `;
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

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 90) current = s.id;
    });
    navLinks.forEach(a => {
      const href = a.getAttribute('href') || '';
      if (href.includes('#' + current)) {
        a.style.color = 'var(--text-primary)';
      } else {
        a.style.color = '';
      }
    });
  }, { passive: true });
})();


(function initScrollTop() {
  const btn = document.getElementById('scrollTop');
  const trigger = document.getElementById('cta');
  if (!btn || !trigger) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        btn.classList.add('visible');
      } else {
        if (window.scrollY < trigger.offsetTop) {
          btn.classList.remove('visible');
        }
      }
    });
  }, { threshold: 0.1 });

  observer.observe(trigger);

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

(function initChatbot() {
  const wrapper   = document.getElementById('chatbotWrapper');
  const toggle    = document.getElementById('chatbotToggle');
  const panel     = document.getElementById('chatbotPanel');
  const closeBtn  = document.getElementById('chatbotClose');
  const input     = document.getElementById('chatbotInput');
  const sendBtn   = document.getElementById('chatbotSend');
  const messages  = document.getElementById('chatbotMessages');
  const suggestions = document.getElementById('chatbotSuggestions');
  const iconOpen  = toggle ? toggle.querySelector('.chatbot-toggle-icon--open')  : null;
  const iconClose = toggle ? toggle.querySelector('.chatbot-toggle-icon--close') : null;
  const trigger   = document.getElementById('cta');

  if (!wrapper || !trigger) return;

  let isPanelOpen = false;

  const visibilityObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        wrapper.classList.add('visible');
      } else {
        if (window.scrollY < trigger.offsetTop) {
          wrapper.classList.remove('visible');
        }
      }
    });
  }, { threshold: 0.1 });

  visibilityObserver.observe(trigger);

  function openPanel() {
    isPanelOpen = true;
    panel.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    if (iconOpen)  iconOpen.style.display  = 'none';
    if (iconClose) iconClose.style.display = '';
    if (input) input.focus();
    scrollMessages();
    const notif = toggle.querySelector('.chatbot-notif');
    if (notif) notif.style.display = 'none';
  }

  function closePanel() {
    isPanelOpen = false;
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    if (iconOpen)  iconOpen.style.display  = '';
    if (iconClose) iconClose.style.display = 'none';
  }

  if (toggle)   toggle.addEventListener('click', () => isPanelOpen ? closePanel() : openPanel());
  if (closeBtn) closeBtn.addEventListener('click', closePanel);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && isPanelOpen) closePanel();
  });

  function scrollMessages() {
    if (messages) {
      setTimeout(() => {
        messages.scrollTop = messages.scrollHeight;
      }, 50);
    }
  }

  function appendMessage(text, role) {
    if (role === 'user' && suggestions) {
      suggestions.style.display = 'none';
    }

    const msg = document.createElement('div');
    msg.className = `chatbot-msg chatbot-msg--${role}`;

    if (role === 'bot') {
      const avatar = document.createElement('div');
      avatar.className = 'chatbot-msg-avatar';
      avatar.setAttribute('aria-hidden', 'true');
      avatar.innerHTML = `
    <div style="height: 24px;width: 24px;"><img height="100%" style="object-fit: contain;" src="{% static 'imgs/bot.png' %}" alt="" srcset=""></div>
    `;
      msg.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = 'chatbot-msg-bubble';
    bubble.innerHTML = text;
    msg.appendChild(bubble);

    messages.appendChild(msg);
    scrollMessages();
  }

  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'chatbot-typing';
    typing.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'chatbot-msg-avatar';
    avatar.setAttribute('aria-hidden', 'true');
    avatar.innerHTML = `
    <div style="height: 24px;width: 24px;"><img height="100%" style="object-fit: contain;" src="{% static 'imgs/bot.png' %}" alt="" srcset=""></div>
    `;
    const dots = document.createElement('div');
    dots.className = 'chatbot-typing-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';

    typing.appendChild(avatar);
    typing.appendChild(dots);
    messages.appendChild(typing);
    scrollMessages();
    return typing;
  }

  function removeTyping() {
    const t = document.getElementById('typingIndicator');
    if (t) t.remove();
  }

  const botResponses = {
    'voir les solutions ia': 'Nous proposons des modèles IA sur mesure, l\'automatisation intelligente des processus, ainsi que notre produit phare <strong>AryadRH</strong>. <a href="#solutions" style="color:var(--accent);">Voir toutes les solutions →</a>',
    'planifier un appel': 'Avec plaisir ! Vous pouvez nous contacter directement à <a href="mailto:contact@aryad.ai" style="color:var(--accent);">contact@aryad.ai</a> ou utiliser le bouton ci-dessous pour planifier un appel stratégique.',
    'en savoir plus sur aryadrh': '<strong>AryadRH</strong> est notre logiciel de gestion RH augmenté par l\'IA — recrutement prédictif, analyse des performances, automatisation administrative. <a href="#product" style="color:var(--accent);">En savoir plus →</a>',
    'default': 'Merci pour votre message ! Notre équipe vous répondra rapidement. En attendant, n\'hésitez pas à <a href="#cta" style="color:var(--accent);">planifier un appel stratégique</a>.',
  };

  function getBotResponse(userText) {
    const key = userText.toLowerCase().trim();
    return botResponses[key] || botResponses['default'];
  }

  function sendMessage(text) {
    if (input) document.getElementById('chatbotInput').value = "";
    const trimmed = text.trim();
    if (!trimmed) return;
    appendMessage(trimmed, 'user');
    if (sendBtn) sendBtn.disabled = true;

    const typingEl = showTyping();

    setTimeout(() => {
      removeTyping();
      appendMessage(getBotResponse(trimmed), 'bot');
      if (input) document.getElementById('chatbotInput').value = "";
      if (sendBtn) sendBtn.disabled = false;
      if (input) input.focus();
    }, 900 + Math.random() * 400);
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', () => {
      if (input) {
        var value = input.value;
        document.getElementById('chatbotInput').value = "";
        sendMessage(value);
      }

    });
  }

  if (input) {
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (input) {
        var value = input.value;
        document.getElementById('chatbotInput').value = "";
        sendMessage(value);
      }
      }
    });
  }

  window.sendSuggestion = function(btn) {
    sendMessage(btn.textContent);
  };
})();