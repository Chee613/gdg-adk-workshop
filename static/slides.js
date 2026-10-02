const slides = [...document.querySelectorAll('.slide')];
const previous = document.getElementById('previous');
const next = document.getElementById('next');
const notesToggle = document.getElementById('notesToggle');
const notesPanel = document.getElementById('notesPanel');
let current = 0;
const bound = n => Math.max(0, Math.min(slides.length - 1, Number.isFinite(n) ? n : 0));
console.assert(bound(-1) === 0 && bound(999) === slides.length - 1 && bound(NaN) === 0, 'Slide bounds');
function show(n) {
  current = bound(n);
  slides.forEach((slide, i) => {
    slide.classList.toggle('active', i === current);
    slide.setAttribute('aria-hidden', String(i !== current));
  });
  document.getElementById('slideCount').textContent = `${String(current + 1).padStart(2, '0')} / ${slides.length}`;
  previous.disabled = current === 0;
  next.disabled = current === slides.length - 1;
  notesPanel.innerHTML = `<h3>Slide ${current + 1} presenter notes</h3>${slides[current].querySelector('.notes').innerHTML}`;
  document.title = `${current + 1}. ${slides[current].dataset.title} | Google ADK workshop`;
  // ponytail: native hashes make individual slides shareable without a router.
  history.replaceState(null, '', `#${current + 1}`);
}
function toggleNotes() {
  notesPanel.hidden = !notesPanel.hidden;
  document.body.classList.toggle('notes-open', !notesPanel.hidden);
  notesToggle.setAttribute('aria-expanded', String(!notesPanel.hidden));
}
previous.addEventListener('click', () => show(current - 1));
next.addEventListener('click', () => show(current + 1));
notesToggle.addEventListener('click', toggleNotes);
document.addEventListener('keydown', e => {
  if (e.target.closest('input, textarea, select, [contenteditable="true"]') || e.ctrlKey || e.altKey || e.metaKey) return;
  if (['ArrowRight', 'PageDown', 'ArrowLeft', 'PageUp', 'Home', 'End'].includes(e.key)) e.preventDefault();
  if (e.key === 'ArrowRight' || e.key === 'PageDown') show(current + 1);
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') show(current - 1);
  if (e.key === 'Home') show(0);
  if (e.key === 'End') show(slides.length - 1);
  if (e.key.toLowerCase() === 'n') toggleNotes();
});
window.addEventListener('hashchange', () => show(Number(location.hash.slice(1)) - 1));
show(Number(location.hash.slice(1)) - 1);
if (location.protocol === 'file:') {
  document.querySelectorAll('[data-demo-link]').forEach(link => link.href = 'http://127.0.0.1:8001/');
}
