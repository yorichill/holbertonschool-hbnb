/* ── HBnB header / auth nav ─────────────────────────────── */
import { deleteCookie } from './utils.js';

/**
 * Injecte le header depuis header.html, marque le lien actif,
 * et branche le bouton Sign In / Sign Out.
 *
 * @param {string|null} token
 * @param {object}      opts
 * @param {string}      [opts.navId='auth-nav-item']
 * @param {string}      [opts.redirectOnLogout='index.html']
 * @param {string}      [opts.activeLink]
 */
export async function initAuthNav(token, {
  navId = 'auth-nav-item',
  redirectOnLogout = 'index.html',
  activeLink = '',
} = {}) {
  const mount = document.getElementById('app-header');
  if (!mount) return;

  /* ── Load header HTML fragment ── */
  try {
    const res  = await fetch('./header.html');
    const html = await res.text();
    mount.innerHTML = html;
  } catch (_) {
    mount.innerHTML = '<nav></nav>';
  }

  /* ── Mark active link ── */
  if (activeLink) {
    const link = mount.querySelector(`a[href="${activeLink}"]`);
    link?.classList.add('active');
  }

  /* ── Inject Sign In / Sign Out ── */
  const nav = mount.querySelector(`#${navId}`);
  if (!nav) return;

  if (token) {
    nav.innerHTML = `
      <a href="#" id="logout-btn" class="login-button" style="background:var(--color-muted)">
        Sign Out
      </a>`;
    document.getElementById('logout-btn').addEventListener('click', (e) => {
      e.preventDefault();
      deleteCookie('token');
      window.location.replace(redirectOnLogout);
    });
  } else {
    nav.innerHTML = `<a href="login.html" class="login-button">Sign In</a>`;
  }
}