// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

navToggle.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', String(isOpen));
});

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});

// Theme toggle with persistence
const themeToggle = document.getElementById('themeToggle');
const root = document.documentElement;

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
  themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

let savedTheme = 'light';
try {
  savedTheme = localStorage.getItem('theme') || 'light';
} catch (e) {
  // localStorage unavailable; default to light theme
}
applyTheme(savedTheme);

themeToggle.addEventListener('click', () => {
  const current = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  applyTheme(current);
  try {
    localStorage.setItem('theme', current);
  } catch (e) {
    // ignore storage failures
  }
});

// Footer year
document.getElementById('year').textContent = new Date().getFullYear();

// Contact form (client-side only placeholder)
const contactForm = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');

contactForm.addEventListener('submit', (e) => {
  e.preventDefault();
  formStatus.textContent = 'Thanks for reaching out! I\'ll get back to you soon.';
  contactForm.reset();
});
