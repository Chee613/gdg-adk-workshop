'use strict';

const byId = id => document.getElementById(id);
let sessionId = null;
let currentMode = 'walkthrough';
let state = { emails: [], drafts: [], pending: [], preferences: {} };
let selectedEmail = null;
let busy = false;

// ponytail: native DOM rendering keeps email and model text inert; no templating dependency.
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function setBusy(value, message = '') {
  busy = value;
  byId('workspace').setAttribute('aria-busy', String(value));
  document.querySelectorAll('[data-request], .draft-editor').forEach(node => {
    node.disabled = value || !sessionId;
  });
  byId('chat-input').disabled = value || !sessionId;
  byId('new-session').disabled = value;
  byId('request-status').textContent = message || (sessionId ? 'Ready when you are.' : 'Start a new session to retry.');
  byId('ask-button').textContent = value ? 'Working…' : 'Ask Buddy';
}

async function request(path, payload) {
  const response = await fetch(path, {
    method: payload === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json', ...(sessionId ? { 'X-Session-ID': sessionId } : {}) },
    ...(payload === undefined ? {} : { body: JSON.stringify(payload) })
  });
  let data;
  try { data = await response.json(); } catch { throw new Error('The server returned an unreadable response. Check the server and try again.'); }
  if (!response.ok) {
    if (data.pending !== undefined) updateState(data);
    const detail = typeof data.detail === 'string' ? data.detail : typeof data.error === 'string' ? data.error : `Request failed (${response.status}).`;
    throw new Error(detail);
  }
  return data;
}

function showError(error) {
  byId('error').textContent = `${error.message || 'Something went wrong.'} Your conversation is still here. Try again when the server is ready.`;
  byId('error').hidden = false;
}

function setMode(mode) {
  currentMode = mode;
  const modes = {
    walkthrough: ['Guided walkthrough • scripted, no AI key', 'Fictional inbox. Replies and tool steps are scripted for learning; no Gemini or Gmail connection.', '#fbbc04'],
    'sample-ai': ['Sample inbox • real ADK + Gemini', 'Fictional email text and your chat are sent to Gemini. Drafts and labels stay in this private sample session.', '#4285f4'],
    'gmail-ai': ['Your Gmail • real ADK + Gemini', 'Retrieved email text and your chat are sent to Gemini. Review and confirm each draft or label before it changes Gmail.', '#34a853']
  };
  const [title, description, colour] = modes[mode] || ['Unknown mode', 'The server did not identify its mode. Check your server configuration.', '#ea4335'];
  byId('mode-title').textContent = title;
  byId('mode-description').textContent = description;
  byId('mode-indicator').style.background = colour;
  byId('inbox-caption').textContent = mode === 'gmail-ai' ? 'Your retrieved Gmail messages' : 'Fictional emails for the workshop';
  byId('drafts-caption').textContent = mode === 'gmail-ai' ? 'Approved drafts saved to Gmail. Nothing is sent.' : 'Approved drafts saved in this sample session.';
}

function tags(labels) {
  const row = element('div', undefined, 'tags');
  (labels || []).forEach(label => row.append(element('span', label, 'tag')));
  return row;
}

function renderEmails() {
  const list = byId('email-list');
  list.replaceChildren();
  byId('email-count').textContent = String(state.emails.length);
  if (!state.emails.length) list.append(element('p', 'No emails loaded. Ask Buddy to check your inbox.', 'empty-state'));
  state.emails.forEach(email => {
    const button = element('button', undefined, 'email-item');
    button.type = 'button';
    button.setAttribute('aria-pressed', String(email.id === selectedEmail));
    const sender = element('span', undefined, 'sender');
    if (email.unread) sender.append(element('span', undefined, 'unread-dot'));
    sender.append(element('span', email.sender));
    button.append(sender, element('span', email.subject, 'subject'), element('span', email.body, 'snippet'), tags(email.labels));
    button.setAttribute('aria-label', `${email.unread ? 'Unread email' : 'Email'} from ${email.sender}: ${email.subject}`);
    button.onclick = () => { selectedEmail = email.id; renderEmails(); renderPreview(); };
    list.append(button);
  });
}

function renderPreview() {
  const preview = byId('email-preview');
  preview.replaceChildren();
  const email = state.emails.find(item => item.id === selectedEmail);
  if (!email) {
    const empty = element('div', undefined, 'empty-state');
    empty.append(element('h3', 'Take a look around.'), element('p', 'Select an email to read it, then ask Buddy for a hand.'));
    preview.append(empty);
    return;
  }
  preview.append(element('h3', email.subject, 'email-subject'), element('p', `From: ${email.sender}`, 'email-sender'), tags(email.labels), element('p', email.body, 'email-body'));
}

async function copyDraft(draft, button) {
  const text = `To: ${draft.to}\nSubject: ${draft.subject}\n\n${draft.body}`;
  try {
    if (!navigator.clipboard) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(text);
    button.textContent = 'Copied';
    byId('request-status').textContent = 'Draft copied to clipboard.';
  } catch {
    const field = element('textarea', text, 'draft-editor');
    field.readOnly = true;
    field.setAttribute('aria-label', 'Draft text to copy manually');
    button.parentElement.append(field);
    field.focus();
    field.select();
    button.textContent = 'Select and copy below';
    button.disabled = true;
    byId('request-status').textContent = 'Copy selected draft text with Ctrl+C or Command+C.';
  }
}

function renderDrafts() {
  const container = byId('saved-drafts');
  container.replaceChildren();
  byId('draft-count').textContent = String(state.drafts.length);
  if (!state.drafts.length) return;
  state.drafts.forEach(draft => {
    const details = element('details', undefined, 'saved-draft');
    details.append(element('summary', draft.subject), element('p', `To: ${draft.to}`), element('p', draft.body, 'draft-body'));
    const copy = element('button', 'Copy draft', 'button');
    copy.type = 'button';
    copy.onclick = () => copyDraft(draft, copy);
    details.append(copy);
    container.append(details);
  });
}

function renderPreferences() {
  const container = byId('preferences');
  container.replaceChildren();
  const entries = Object.entries(state.preferences || {});
  if (!entries.length) { container.textContent = 'No preferences saved yet.'; return; }
  const list = element('dl');
  entries.forEach(([key, value]) => list.append(element('dt', key.replaceAll('_', ' ')), element('dd', typeof value === 'string' ? value : JSON.stringify(value))));
  container.append(list);
}

function renderPending() {
  const container = byId('pending-actions');
  container.replaceChildren();
  state.pending.forEach(action => {
    const card = element('section', undefined, 'action-proposal');
    const draft = action.kind === 'draft';
    card.append(element('h3', draft ? 'Review your reply' : 'Review a label change'), element('p', 'Waiting for your confirmation.'));
    let editor;
    if (draft) {
      card.append(element('p', `To: ${action.to || ''}`), element('p', `Subject: ${action.subject || ''}`));
      const label = element('label', 'Edit your draft');
      editor = element('textarea', action.body || '', 'draft-editor');
      editor.id = `draft-${action.id}`;
      label.htmlFor = editor.id;
      editor.rows = 6;
      editor.required = true;
      card.append(label, editor, element('p', currentMode === 'gmail-ai' ? 'Confirmation saves a draft to Gmail. It does not send it.' : 'Confirmation saves a draft in this sample session.'));
    } else {
      const email = state.emails.find(item => item.id === action.message_id);
      card.append(element('p', `Apply “${action.label || ''}” to “${email?.subject || action.message_id || 'email'}”?`));
    }
    const controls = element('div', undefined, 'action-buttons');
    const approve = element('button', draft ? 'Confirm & save draft' : 'Confirm label', 'button primary');
    const decline = element('button', 'Decline', 'button');
    [approve, decline].forEach(button => { button.type = 'button'; button.dataset.request = ''; });
    approve.onclick = () => {
      if (editor && !editor.value.trim()) { editor.focus(); byId('request-status').textContent = 'Add a reply before saving the draft.'; return; }
      resolveAction(action.id, 'approve', editor ? { body: editor.value } : {});
    };
    decline.onclick = () => resolveAction(action.id, 'decline', {});
    controls.append(approve, decline);
    card.append(controls);
    container.append(card);
  });
}

function updateState(data) {
  // ponytail: the API owns session state; the page keeps only the current snapshot.
  for (const key of ['emails', 'drafts', 'pending', 'preferences']) {
    if (data[key] !== undefined) state[key] = data[key];
  }
  if (!state.emails.some(email => email.id === selectedEmail)) selectedEmail = state.emails[0]?.id || null;
  renderEmails();
  renderPreview();
  renderDrafts();
  renderPreferences();
  renderPending();
}

function addMessage(text, role, activity = []) {
  const message = element('div', undefined, `chat-message ${role}`);
  message.append(element('p', role === 'user' ? 'You' : 'Inbox Buddy', 'speaker'), element('p', text));
  if (activity.length) {
    const details = element('details', undefined, 'activity');
    details.append(element('summary', currentMode === 'walkthrough' ? `Scripted tool steps (${activity.length})` : `Tool activity (${activity.length})`));
    const list = element('ul', undefined, 'activity-list');
    activity.forEach(item => {
      const row = element('li');
      row.append(element('strong', item.tool), element('span', item.summary), element('span', item.status || 'completed', `activity-status ${['error', 'failed'].includes(item.status) ? 'error' : ''}`));
      list.append(row);
    });
    details.append(list);
    message.append(details);
  }
  byId('conversation').append(message);
  byId('conversation').scrollTop = byId('conversation').scrollHeight;
}

async function startSession() {
  if (busy) return;
  setBusy(true, 'Starting a fresh private session…');
  byId('error').hidden = true;
  try {
    const data = await request('/api/session', {});
    if (!data.session_id) throw new Error('The server did not return a session ID.');
    sessionId = data.session_id;
    state = { emails: [], drafts: [], pending: [], preferences: {} };
    selectedEmail = null;
    byId('conversation').replaceChildren();
    byId('chat-input').value = '';
    setMode(data.mode);
    updateState(data);
    addMessage(data.mode === 'walkthrough' ? 'Hi! This guided walkthrough uses fictional emails and scripted replies. Try one of the prompts below. You’ll review any draft or label before it’s saved.' : 'Hi! I’m your ADK-powered Inbox Buddy. Ask me to summarize your inbox or draft a reply. You’ll review any draft or label before it’s saved.', 'assistant');
    setBusy(false, 'New private session ready.');
  } catch (error) {
    showError(error);
    if (!sessionId) {
      byId('mode-title').textContent = 'Could not start the session';
      byId('mode-description').textContent = 'Check that the workshop server is running, then choose New private session.';
    }
    setBusy(false);
  }
}

async function chat(message) {
  if (busy || !sessionId || !message.trim()) return;
  setBusy(true, currentMode === 'walkthrough' ? 'Playing the guided tool steps…' : 'Buddy is working…');
  byId('error').hidden = true;
  addMessage(message, 'user');
  try {
    const data = await request('/api/chat', { message });
    updateState(data);
    addMessage(data.reply || 'Done. Review the updated inbox and any proposals below.', 'assistant', data.activity || []);
    byId('chat-input').value = '';
    setBusy(false, state.pending.length ? 'A proposal is ready for your review.' : 'Ready when you are.');
    if (state.pending.length) byId('pending-actions').scrollIntoView({ block: 'nearest', behavior: 'auto' });
    byId('chat-input').focus({ preventScroll: true });
  } catch (error) { showError(error); setBusy(false, 'Request failed. Your message and conversation are preserved.'); }
}

async function resolveAction(id, resolution, payload) {
  if (busy) return;
  setBusy(true, resolution === 'approve' ? 'Saving your confirmed action…' : 'Declining the proposal…');
  byId('error').hidden = true;
  try {
    const data = await request(`/api/actions/${encodeURIComponent(id)}/${resolution}`, payload);
    updateState(data);
    addMessage(data.reply || (resolution === 'approve' ? 'Saved your confirmed action.' : 'Declined. No change was made.'), 'assistant', data.activity || []);
    setBusy(false, resolution === 'approve' ? 'Your confirmed action was saved.' : 'Proposal declined.');
    byId('chat-input').focus({ preventScroll: true });
  } catch (error) { showError(error); setBusy(false, 'Action failed. Your proposal is still available to review.'); }
}

byId('new-session').onclick = startSession;
byId('chat-form').onsubmit = event => { event.preventDefault(); chat(byId('chat-input').value.trim()); };
document.querySelectorAll('[data-prompt]').forEach(button => { button.onclick = () => chat(button.textContent); });
byId('chat-input').addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); chat(byId('chat-input').value.trim()); }
});
startSession();
