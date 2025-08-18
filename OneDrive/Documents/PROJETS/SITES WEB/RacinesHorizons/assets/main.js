// Mobile nav toggle
const navToggleButton = document.querySelector('.nav-toggle');
const siteNav = document.getElementById('site-nav');
if (navToggleButton && siteNav) {
  navToggleButton.addEventListener('click', () => {
    const expanded = navToggleButton.getAttribute('aria-expanded') === 'true';
    navToggleButton.setAttribute('aria-expanded', String(!expanded));
    siteNav.setAttribute('aria-expanded', String(!expanded));
  });
}

// Fade-in on scroll
const fadeElements = document.querySelectorAll('.fade-in');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12 });
  fadeElements.forEach((el) => observer.observe(el));
} else {
  fadeElements.forEach((el) => el.classList.add('visible'));
}

// Smooth scroll for same-page anchors
const anchorLinks = document.querySelectorAll('a[href^="#"]');
for (const link of anchorLinks) {
  link.addEventListener('click', (e) => {
    const href = link.getAttribute('href');
    if (!href || href === '#') return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
}
