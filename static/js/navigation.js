/**
 * BUILD+ Navigation and Header Interactivity
 * Handles sticky navbar scroll state, mega menu keyboard access & transitions
 */
document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    // Handle scroll compacting and shadow
    const handleScroll = () => {
        if (window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    // Mega menu keyboard navigation and hover enhancement for desktop
    const megaMenuDropdown = document.querySelector('.has-mega-menu');
    if (megaMenuDropdown) {
        const toggle = megaMenuDropdown.querySelector('.dropdown-toggle');
        const menu = megaMenuDropdown.querySelector('.mega-menu-dropdown');

        if (toggle && menu) {
            // Support ESC key to close
            megaMenuDropdown.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                    if (bsDropdown) bsDropdown.hide();
                    toggle.focus();
                }
            });
        }
    }
});
