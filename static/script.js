// Elements
const input = document.getElementById('messageInput');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusEl = document.getElementById('status');
const sentCountEl = document.getElementById('sentCount');

let pollId = null;

async function callStart(message, intervalMs = 200) {
  try {
    const resp = await fetch('/publisher_app/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, interval_ms: intervalMs })
    });
    return resp.json();
  } catch (e) {
    return { status: 'error', message: 'network error' };
  }
}

async function callStop() {
  try {
    const resp = await fetch('/publisher_app/stop', { method: 'POST' });
    return resp.json();
  } catch (e) {
    return { status: 'error', message: 'network error' };
  }
}

async function getStatus() {
  try {
    const resp = await fetch('/publisher_app/status');
    return resp.json();
  } catch (e) {
    return { running: false };
  }
}

function startPolling() {
  if (pollId) return;
  pollId = setInterval(async () => {
    const s = await getStatus();
    sentCountEl.textContent = String(s.sent_count || 0);
    statusEl.textContent = s.running ? 'Running' : 'Stopped';
  }, 300);
}

function stopPolling() {
  if (!pollId) return;
  clearInterval(pollId);
  pollId = null;
}

startBtn.addEventListener('click', async () => {
  const message = (input.value || '').trim();
  if (!message) {
    statusEl.textContent = 'Enter a message before starting';
    return;
  }
  startBtn.disabled = true;
  stopBtn.disabled = false;
  input.disabled = true;
  statusEl.textContent = 'Starting...';
  const res = await callStart(message, 200);
  if (res && res.status === 'ok') {
    statusEl.textContent = 'Running';
    sentCountEl.textContent = '0';
    startPolling();
  } else {
    statusEl.textContent = 'Start failed: ' + (res.message || 'unknown');
    startBtn.disabled = false;
    stopBtn.disabled = true;
    input.disabled = false;
  }
});

stopBtn.addEventListener('click', async () => {
  stopBtn.disabled = true;
  statusEl.textContent = 'Stopping...';
  const res = await callStop();
  stopPolling();
  startBtn.disabled = false;
  input.disabled = false;
  if (res && res.status === 'ok') {
    statusEl.textContent = `Stopped. Sent ${res.sent_count || 0}`;
    sentCountEl.textContent = String(res.sent_count || 0);
  } else {
    statusEl.textContent = 'Stop failed: ' + (res.message || 'unknown');
  }
});
