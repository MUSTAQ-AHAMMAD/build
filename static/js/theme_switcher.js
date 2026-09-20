/**
 * BUILD+ Universal Theme Switcher (Light, Dark, System)
 * Persists theme preference across Public Website, Master Admin, CMS, CRM, AI, Payments, and Client Portal
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'buildplus_theme_preference';

    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function getSavedPreference() {
        return localStorage.getItem(STORAGE_KEY) || 'system';
    }

    function applyTheme(preference) {
        const effectiveTheme = preference === 'system' ? getSystemTheme() : preference;
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        document.documentElement.setAttribute('data-bs-theme', effectiveTheme);
        document.documentElement.setAttribute('data-theme-preference', preference);
        
        document.querySelectorAll('.theme-btn').forEach(btn => {
            if (btn.getAttribute('data-theme-val') === preference) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        const label = document.getElementById('currentThemeLabel');
        if (label) {
            if (preference === 'dark') label.innerHTML = '🌙 Dark';
            else if (preference === 'light') label.innerHTML = '☀ Light';
            else label.innerHTML = '🖥 System';
        }
    }

    const initialPref = getSavedPreference();
    applyTheme(initialPref);

    window.setThemePreference = function(pref) {
        localStorage.setItem(STORAGE_KEY, pref);
        applyTheme(pref);
    };

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (getSavedPreference() === 'system') {
            applyTheme('system');
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        applyTheme(getSavedPreference());
    });
})();
