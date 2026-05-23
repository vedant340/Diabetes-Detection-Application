/* ============================================================
   MediAI — Global JavaScript
   Handles: animations, toasts, tooltips, active nav, forms
   ============================================================ */

'use strict';

// ── DOM Ready ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initCardHovers();
  initNavHighlight();
  initToasts();
  initFormEnhancements();
  initProgressBars();
  animateNumbers();
});

// ── Card hover lift (fallback for CSS) ───────────────────────
function initCardHovers() {
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-2px)';
      card.style.boxShadow = '0 4px 20px rgba(26,35,50,.10)';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
      card.style.boxShadow = '';
    });
  });
}

// ── Sidebar active link highlight ────────────────────────────
function initNavHighlight() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
}

// ── Toast notification system ─────────────────────────────────
function initToasts() {
  // Create container if not present
  if (!document.getElementById('toast-container')) {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
}

/**
 * Show a toast notification
 * @param {string} message  - Text to display
 * @param {'success'|'error'|'info'} type
 * @param {number} duration - ms before auto-dismiss (default 3500)
 */
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
  toast.style.cursor = 'pointer';
  toast.addEventListener('click', () => dismissToast(toast));

  container.appendChild(toast);

  setTimeout(() => dismissToast(toast), duration);
}

function dismissToast(toast) {
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(16px)';
  toast.style.transition = 'opacity .25s, transform .25s';
  setTimeout(() => toast.remove(), 260);
}

// ── Form enhancements ─────────────────────────────────────────
function initFormEnhancements() {
  // Auto-focus first input on forms
  const firstInput = document.querySelector('.form-input:not([type=hidden])');
  if (firstInput && !firstInput.value) firstInput.focus();

  // Animate submit buttons on click
  document.querySelectorAll('button[type=submit]').forEach(btn => {
    btn.addEventListener('click', function () {
      const originalText = this.innerHTML;
      if (this.dataset.loading) return;
      this.dataset.loading = '1';
      this.style.opacity = '.8';
      this.style.pointerEvents = 'none';
      // Restore if form validation fails (500ms grace)
      setTimeout(() => {
        if (document.readyState !== 'loading') {
          this.removeAttribute('data-loading');
          this.style.opacity = '';
          this.style.pointerEvents = '';
        }
      }, 5000);
    });
  });

  // Range slider live value display
  document.querySelectorAll('input[type=range]').forEach(slider => {
    const display = document.getElementById(slider.id + '-val');
    if (display) {
      slider.addEventListener('input', () => { display.textContent = slider.value; });
    }
  });

  // Number input: highlight on focus
  document.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('focus', function () {
      this.style.borderColor = 'var(--teal)';
      this.style.boxShadow = '0 0 0 3px rgba(43,191,160,.12)';
    });
    inp.addEventListener('blur', function () {
      this.style.borderColor = '';
      this.style.boxShadow = '';
    });
  });
}

// ── Animate progress bars on page load ───────────────────────
function initProgressBars() {
  document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => {
        bar.style.width = bar.dataset.width + '%';
      }, 200);
    });
  });
}

// ── Animate counter numbers ───────────────────────────────────
function animateNumbers() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el     = entry.target;
        const target = parseFloat(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const duration = 1200;
        const step   = 16;
        const steps  = duration / step;
        let current  = 0;
        const increment = target / steps;

        const timer = setInterval(() => {
          current += increment;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          el.textContent = (Number.isInteger(target)
            ? Math.round(current)
            : current.toFixed(1)) + suffix;
        }, step);

        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  counters.forEach(el => observer.observe(el));
}

// ── Smooth scroll for anchor links ───────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── Sidebar collapse on mobile ────────────────────────────────
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar       = document.querySelector('.sidebar');
const mainContent   = document.querySelector('.main');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    mainContent && mainContent.classList.toggle('sidebar-open');
  });
  // Close on outside click
  document.addEventListener('click', e => {
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        e.target !== sidebarToggle) {
      sidebar.classList.remove('open');
      mainContent && mainContent.classList.remove('sidebar-open');
    }
  });
}

// ── Confirm on destructive actions ───────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});

// ── Auto-dismiss alerts after 6 seconds ──────────────────────
document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity .4s, max-height .4s';
    alert.style.opacity    = '0';
    alert.style.maxHeight  = '0';
    alert.style.overflow   = 'hidden';
    setTimeout(() => alert.remove(), 420);
  }, 6000);
});

// ── Keyboard shortcut: Ctrl+K → focus search (future) ────────
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const search = document.getElementById('global-search');
    if (search) search.focus();
  }
});

// ── Chart.js global defaults ──────────────────────────────────
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family  = "'DM Sans', sans-serif";
  Chart.defaults.font.size    = 12;
  Chart.defaults.color        = '#8FA0B4';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;
  Chart.defaults.plugins.tooltip.backgroundColor = '#1A2332';
  Chart.defaults.plugins.tooltip.titleColor      = '#E2E8F0';
  Chart.defaults.plugins.tooltip.bodyColor       = '#94A3B8';
  Chart.defaults.plugins.tooltip.cornerRadius    = 10;
  Chart.defaults.plugins.tooltip.padding         = 10;
  Chart.defaults.plugins.tooltip.titleFont       = { family: "'DM Sans'", weight: '700', size: 13 };
  Chart.defaults.plugins.tooltip.bodyFont        = { family: "'DM Sans'", size: 12 };
  Chart.defaults.animation.duration              = 700;
  Chart.defaults.animation.easing               = 'easeInOutQuart';
}

// ── BMI calculator (used on dashboard) ───────────────────────
function calcBMI() {
  const h   = parseFloat(document.getElementById('bmiH')?.value) || 170;
  const w   = parseFloat(document.getElementById('bmiW')?.value) || 65;
  const bmi = (w / ((h / 100) ** 2)).toFixed(1);

  const valEl = document.getElementById('bmiVal');
  const catEl = document.getElementById('bmiCat');
  if (!valEl || !catEl) return;

  valEl.textContent = bmi;

  let cat, color;
  if      (bmi < 18.5) { cat = 'Underweight 🟡'; color = 'var(--warn)'; }
  else if (bmi < 25)   { cat = 'Normal Weight ✅'; color = 'var(--teal)'; }
  else if (bmi < 30)   { cat = 'Overweight 🟠';   color = 'var(--warn)'; }
  else                 { cat = 'Obese 🔴';         color = 'var(--danger)'; }

  catEl.textContent   = cat;
  valEl.style.color   = color;

  const result = document.getElementById('bmiResult');
  if (result) {
    result.style.borderColor = color.replace('var(', '').replace(')', '');
  }
}

// ── Tab switcher (used on info page) ─────────────────────────
function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(el => {
    el.style.display = 'none';
  });
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.style.background    = 'var(--surface)';
    btn.style.color         = 'var(--text2)';
    btn.style.borderColor   = 'var(--border)';
    btn.style.fontWeight    = '500';
  });

  const tab = document.getElementById(id);
  if (tab) tab.style.display = 'block';

  const btn = document.getElementById('tab-' + id);
  if (btn) {
    btn.style.background  = 'var(--teal-lt)';
    btn.style.color       = 'var(--teal)';
    btn.style.borderColor = 'var(--teal-mid)';
    btn.style.fontWeight  = '700';
  }
}