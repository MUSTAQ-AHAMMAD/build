/* ==============================================================================
   BUILD+ THEME MANAGER (LIGHT / DARK THEME + LOCALSTORAGE SYNC)
   ============================================================================== */

(function () {
    const THEME_KEY = 'buildplus_theme';

    function getPreferredTheme() {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored) return stored;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        updateThemeButtons(theme);
    }

    function updateThemeButtons(theme) {
        const buttons = document.querySelectorAll('.theme-toggle-btn');
        buttons.forEach(btn => {
            if (theme === 'dark') {
                btn.innerHTML = '☀️';
                btn.setAttribute('title', 'Switch to Light Mode');
                btn.setAttribute('aria-label', 'Switch to Light Mode');
            } else {
                btn.innerHTML = '🌙';
                btn.setAttribute('title', 'Switch to Dark Mode');
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
            }
        });
    }

    // Apply on earliest script load
    const currentTheme = getPreferredTheme();
    setTheme(currentTheme);

    document.addEventListener('DOMContentLoaded', () => {
        updateThemeButtons(currentTheme);

        document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const active = document.documentElement.getAttribute('data-theme') || 'light';
                const next = active === 'dark' ? 'light' : 'dark';
                setTheme(next);
            });
        });

        // Listen for OS preference change
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem(THEME_KEY)) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    });
})();
