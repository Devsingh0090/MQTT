// Send the text input to the Flask backend which will publish to MQTT
document.getElementById('sendBtn').addEventListener('click', async function () {
  const input = document.getElementById('messageInput');
  const status = document.getElementById('status');
  const message = input.value || '';
  if (!message.trim()) {
    status.textContent = 'Please enter a message';
    return;
  }

  status.textContent = 'Sending...';

  try {
    const resp = await fetch('/publisher_app/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await resp.json();
    if (resp.ok && data.status === 'ok') {
      status.textContent = 'Message sent to printer queue';
      input.value = '';
    } else {
      status.textContent = 'Error: ' + (data.message || 'unknown');
    }
  } catch (err) {
    status.textContent = 'Network error';
  }
});
