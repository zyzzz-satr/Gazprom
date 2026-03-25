(() => {
  const apiBase = '';
  const loader = document.getElementById('loader');
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).slice(2, 9);
    localStorage.setItem('session_id', sessionId);
  }

  const modeBtn = document.getElementById('modeToggle');
  let currentMode = 'OFFLINE';
  fetch('/config').then(r => r.json()).then(d => {
    currentMode = (d.mode || 'OFFLINE').toUpperCase();
    modeBtn.textContent = currentMode;
  });

  modeBtn.addEventListener('click', () => {
    currentMode = (currentMode === 'OFFLINE') ? 'ONLINE' : 'OFFLINE';
    modeBtn.textContent = currentMode;
    fetch('/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({mode: currentMode}) });
  });

  const chat = document.getElementById('chat');
  const inputForm = document.getElementById('inputForm');
  const userInput = document.getElementById('userInput');
  const stageEl = document.getElementById('stage');
  const objectionEl = document.getElementById('objection');
  const repliesEl = document.getElementById('replies');
  const tacticEl = document.getElementById('tactic');
  const nextStepEl = document.getElementById('nextStep');
  const analyticsPanel = document.getElementById('notifications-panel');

  function addMessage(role, text) {
    const row = document.createElement('div');
    row.className = 'message-row';
    const bubble = document.createElement('div');
    bubble.textContent = text;
    if (role === 'client') {
      row.style.justifyContent = 'flex-start';
      bubble.className = 'message-bubble message-client';
    } else {
      row.style.justifyContent = 'flex-end';
      bubble.className = 'message-bubble message-manager';
    }
    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  async function postMessage(text) {
    addMessage('client', text);
    // clear input
    userInput.value = '';
    // show loader
    loader.classList.remove('hidden');
    const resp = await fetch('/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, client_message: text }),
    });
    const data = await resp.json();
    // hide loader
    loader.classList.add('hidden');
    // render AI panel
    stageEl.textContent = data.stage || '-';
    objectionEl.textContent = data.objection_type || '-';
    tacticEl.textContent = data.tactic || '-';
    nextStepEl.textContent = data.next_step || '-';
    // render reply options
    repliesEl.innerHTML = '';
    (data.reply_options || []).forEach((r, idx) => {
      const card = document.createElement('div');
      card.className = 'bg-gray-50 border rounded p-3 flex items-center justify-between card-hover transition-all duration-200';
      const span = document.createElement('span');
      span.textContent = r;
      const copyBtn = document.createElement('button');
      copyBtn.textContent = 'Копировать';
      copyBtn.className = 'ml-2 px-2 py-1 rounded bg-white border text-sm';
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(r);
      });
      const insertBtn = document.createElement('button');
      insertBtn.textContent = 'Вставить в чат';
      insertBtn.className = 'ml-2 px-3 py-1 rounded bg-[#0072CE] text-white hover:bg-[#005BB5] text-sm';
      insertBtn.addEventListener('click', () => {
        postMessage(r);
      });
      card.appendChild(span);
      const actions = document.createElement('div');
      actions.appendChild(copyBtn);
      actions.appendChild(insertBtn);
      card.appendChild(actions);
      // highlight best reply if provided by server
      if (data.best_reply && r === data.best_reply) {
        card.style.border = '2px solid #1e40af';
        card.style.boxSizing = 'border-box';
      }
      repliesEl.appendChild(card);
    });
  }

  inputForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (userInput.value.trim()) postMessage(userInput.value.trim());
  });

  // initial hint
  addMessage('manager', 'Готов помочь вернуть клиента — начнем с текущего запроса.');

  // Load analytics on startup
  async function loadAnalytics() {
    try {
      const resp = await fetch(`/analytics?session_id=${sessionId}`);
      const data = await resp.json();
      document.getElementById('analytics-daily').textContent = data.daily_volume ?? '-';
      document.getElementById('analytics-avg').textContent = (data.avg_handle_time_ms ?? '-') + ' ms';
      document.getElementById('analytics-conv').textContent = Math.round((data.conversion_rate ?? 0) * 100) + '%';
      const top = data.top_clients ?? [];
      const topEl = document.getElementById('analytics-top');
      topEl.textContent = top.map(c => c.name + ': ' + (c.amount || 0)).join(', ');
      // Populate notifications from analytics data (optional placeholder)
      // Show a sample notification if not present
    } catch (e) {
      // ignore analytics load errors
    }
  }
  loadAnalytics();
  
  // Toggle notifications panel from header (bind once we know header element)
  const notifBtn = document.getElementById('notif-button');
  if (notifBtn) {
    notifBtn.addEventListener('click', () => {
      analyticsPanel.style.display = analyticsPanel.style.display === 'none' ? 'block' : 'none';
    });
  }
})();
