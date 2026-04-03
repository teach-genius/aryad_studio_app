/**
 * visitor.js — ARYAD Visitor Tracking & Chat API
 * -----------------------------------------------
 * Prérequis : window.ARYAD_CONFIG doit être défini dans base.html
 * avant le chargement de ce fichier :
 *
 *   <script>
 *     window.ARYAD_CONFIG = {
 *       botAvatarUrl: "{% static 'imgs/bot.png' %}",
 *     };
 *   </script>
 *
 * L'URL de l'image est résolue par Django dans le template HTML,
 * puis transmise au JS via window.ARYAD_CONFIG — les fichiers .js
 * statiques ne sont PAS traités par le moteur de templates Django.
 */

(function () {
  'use strict';

  /* ═══════════════════════════════════════
     CONSTANTES
     ═══════════════════════════════════════ */

  const VISITOR_KEY    = 'aryad_visitor_uid';
  const CONV_KEY       = 'aryad_conversation_id';
  const REGISTER_URL   = '/api/visitor/register/';
  const CHAT_URL       = '/api/chat/';
  const GEO_API_URL    = 'https://ipapi.co/json/';
  const GEO_TIMEOUT_MS = 4000;

  // URL de l'avatar bot — fournie par base.html via window.ARYAD_CONFIG
  function getBotAvatarUrl() {
    return (window.ARYAD_CONFIG && window.ARYAD_CONFIG.botAvatarUrl)
      ? window.ARYAD_CONFIG.botAvatarUrl
      : '';
  }

  // HTML de l'avatar bot (réutilisé dans appendMsg et showTyping)
  function botAvatarHTML() {
    const url = getBotAvatarUrl();
    if (!url) {
      // Fallback : initiale "A" si l'image n'est pas configurée
      return 'A';
    }
    return `<div style="height:24px;width:24px;">
              <img height="100%" style="object-fit:contain;" src="${url}" alt="Bot ARYAD">
            </div>`;
  }

  /* ═══════════════════════════════════════
     1. VISITOR UID  (localStorage)
     ═══════════════════════════════════════ */

  function getOrCreateVisitorUid() {
    let uid = localStorage.getItem(VISITOR_KEY);
    if (!uid) {
      uid = (typeof crypto !== 'undefined' && crypto.randomUUID)
        ? crypto.randomUUID()
        : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = (Math.random() * 16) | 0;
            return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
          });
      localStorage.setItem(VISITOR_KEY, uid);
    }
    return uid;
  }

  /* ═══════════════════════════════════════
     2. DEVICE DETECTION
     ═══════════════════════════════════════ */

  function getDeviceType() {
    const ua = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(ua))                         return 'tablet';
    if (/mobile|android|iphone|ipod|blackberry|opera mini/i.test(ua))  return 'mobile';
    return 'desktop';
  }

  function getBrowser() {
    const ua = navigator.userAgent;
    if (ua.includes('Edg'))     return 'Edge';
    if (ua.includes('OPR'))     return 'Opera';
    if (ua.includes('Chrome'))  return 'Chrome';
    if (ua.includes('Firefox')) return 'Firefox';
    if (ua.includes('Safari'))  return 'Safari';
    return 'Unknown';
  }

  function getOS() {
    const ua = navigator.userAgent;
    if (ua.includes('Windows'))                        return 'Windows';
    if (ua.includes('Mac'))                            return 'macOS';
    if (ua.includes('Android'))                        return 'Android';
    if (ua.includes('iPhone') || ua.includes('iPad')) return 'iOS';
    if (ua.includes('Linux'))                          return 'Linux';
    return 'Unknown';
  }

  /* ═══════════════════════════════════════
     3. UTM PARAMS
     ═══════════════════════════════════════ */

  function getUTMParams() {
    const p = new URLSearchParams(window.location.search);
    return {
      utm_source:   p.get('utm_source')   || '',
      utm_medium:   p.get('utm_medium')   || '',
      utm_campaign: p.get('utm_campaign') || '',
    };
  }

  /* ═══════════════════════════════════════
     4. TIMEZONE & LANGUE
     ═══════════════════════════════════════ */

  function getTimezone() {
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }
    catch (_) { return ''; }
  }

  function getLanguage() {
    return navigator.language || navigator.userLanguage || '';
  }

  /* ═══════════════════════════════════════
     5. GÉOLOCALISATION via ipapi.co
     ═══════════════════════════════════════ */

  async function fetchGeo() {
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), GEO_TIMEOUT_MS);
      const res = await fetch(GEO_API_URL, { signal: controller.signal });
      clearTimeout(tid);
      if (!res.ok) return {};
      const d = await res.json();
      return {
        country:      d.country_name || '',
        country_code: d.country_code || '',
        city:         d.city         || '',
        region:       d.region       || '',
        latitude:     d.latitude     || null,
        longitude:    d.longitude    || null,
      };
    } catch (_) {
      return {};
    }
  }

  /* ═══════════════════════════════════════
     6. REGISTER VISITOR
     ═══════════════════════════════════════ */

  async function registerVisitor() {
    const uid  = getOrCreateVisitorUid();
    const utms = getUTMParams();
    const geo  = await fetchGeo();

    const payload = {
      visitor_uid:   uid,
      device_type:   getDeviceType(),
      browser:       getBrowser(),
      os:            getOS(),
      screen_width:  window.screen.width,
      screen_height: window.screen.height,
      language:      getLanguage(),
      timezone:      getTimezone(),
      referrer:      document.referrer || '',
      landing_page:  window.location.pathname,
      ...utms,
      ...geo,
    };

    try {
      const res  = await fetch(REGISTER_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.visitor_uid) {
        localStorage.setItem(VISITOR_KEY, data.visitor_uid);
      }
      window.ARYAD_VISITOR_UID = data.visitor_uid || uid;
    } catch (err) {
      console.warn('[ARYAD] register_visitor failed:', err);
      window.ARYAD_VISITOR_UID = uid;
    }
  }

  /* ═══════════════════════════════════════
     7. CHAT API
     ═══════════════════════════════════════ */

  async function sendMessageToAPI(userText) {
    const payload = {
      message:         userText,
      visitor_uid:     localStorage.getItem(VISITOR_KEY) || '',
      conversation_id: localStorage.getItem(CONV_KEY)    || null,
    };

    const res  = await fetch(CHAT_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.conversation_id) localStorage.setItem(CONV_KEY, data.conversation_id);
    if (data.visitor_uid) {
      localStorage.setItem(VISITOR_KEY, data.visitor_uid);
      window.ARYAD_VISITOR_UID = data.visitor_uid;
    }
    if (data.status !== 'ok') throw new Error(data.error || 'Erreur serveur');
    return data.reply;
  }

  window.ARYAD_SEND_MESSAGE = sendMessageToAPI;

  /* ═══════════════════════════════════════
     8. PATCH CHATBOT
        Remplace les réponses statiques d'aryad.js
        par de vrais appels à /api/chat/
        et injecte l'avatar image bot.
     ═══════════════════════════════════════ */

  function patchChatbot() {
    const input    = document.getElementById('chatbotInput');
    const sendBtn  = document.getElementById('chatbotSend');
    const messages = document.getElementById('chatbotMessages');
    if (!input || !sendBtn || !messages) return;

    // ── Met à jour l'avatar bot initial dans le message de bienvenue ──
    document.querySelectorAll('.chatbot-msg--bot .chatbot-msg-avatar').forEach(el => {
      el.innerHTML = botAvatarHTML();
    });

    function scrollMessages() {
      setTimeout(() => { messages.scrollTop = messages.scrollHeight; }, 50);
    }

    function appendMsg(html, role) {
      const msg = document.createElement('div');
      msg.className = `chatbot-msg chatbot-msg--${role}`;

      if (role === 'bot') {
        const avatar = document.createElement('div');
        avatar.className = 'chatbot-msg-avatar';
        avatar.setAttribute('aria-hidden', 'true');
        avatar.innerHTML = botAvatarHTML();
        msg.appendChild(avatar);
      }

      const bubble = document.createElement('div');
      bubble.className = 'chatbot-msg-bubble';
      bubble.innerHTML = html;
      msg.appendChild(bubble);

      messages.appendChild(msg);
      scrollMessages();
    }

    function showTyping() {
      const el = document.createElement('div');
      el.className = 'chatbot-typing';
      el.id = 'typingIndicator';

      const avatar = document.createElement('div');
      avatar.className = 'chatbot-msg-avatar';
      avatar.setAttribute('aria-hidden', 'true');
      avatar.innerHTML = botAvatarHTML();

      const dots = document.createElement('div');
      dots.className = 'chatbot-typing-dots';
      dots.innerHTML = '<span></span><span></span><span></span>';

      el.appendChild(avatar);
      el.appendChild(dots);
      messages.appendChild(el);
      scrollMessages();
    }

    function removeTyping() {
      const t = document.getElementById('typingIndicator');
      if (t) t.remove();
    }

    // Remplacer les event listeners existants (cloner les éléments)
    const newSend  = sendBtn.cloneNode(true);
    const newInput = input.cloneNode(true);
    sendBtn.parentNode.replaceChild(newSend,  sendBtn);
    input.parentNode.replaceChild(newInput, input);

    // sendMessage utilise newInput directement — plus de référence à l'ancien input
    async function sendMessage(text) {
      const trimmed = (text || '').trim();
      if (!trimmed) return;

      const suggestions = document.getElementById('chatbotSuggestions');
      if (suggestions) suggestions.style.display = 'none';

      appendMsg(trimmed, 'user');
      newInput.value   = '';          // ← vide le bon élément
      newInput.focus();
      newSend.disabled = true;
      showTyping();

      try {
        const reply = await sendMessageToAPI(trimmed);
        removeTyping();
        appendMsg(reply, 'bot');
      } catch (err) {
        removeTyping();
        appendMsg(
          "Une erreur est survenue. Veuillez réessayer ou nous <a href='#cta' style='color:var(--accent)'>contacter directement</a>.",
          'bot'
        );
        console.error('[ARYAD] chat error:', err);
      } finally {
        newSend.disabled = false;
        newInput.focus();
      }
    }

    newSend.addEventListener('click', () => sendMessage(newInput.value));
    newInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); sendMessage(newInput.value); }
    });

    window.sendSuggestion = btn => sendMessage(btn.textContent);
  }

  /* ═══════════════════════════════════════
     INIT
     ═══════════════════════════════════════ */

  document.addEventListener('DOMContentLoaded', () => {
    registerVisitor();   // async — non bloquant
    patchChatbot();
  });

})();