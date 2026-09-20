/* ==============================================================================
   BUILD+ DYNAMIC CLIENT-SIDE FILTERS (PROJECTS & BLOGS)
   ============================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Projects Filter
    const projectFilterButtons = document.querySelectorAll('.project-filter-btn');
    const projectItems = document.querySelectorAll('.project-item');
    const noProjectsMessage = document.getElementById('noProjectsMessage');

    if (projectFilterButtons.length > 0 && projectItems.length > 0) {
        projectFilterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update Active Button State
                projectFilterButtons.forEach(b => b.classList.remove('active', 'btn-primary-custom'));
                projectFilterButtons.forEach(b => b.classList.add('btn-outline-custom'));
                btn.classList.add('active', 'btn-primary-custom');
                btn.classList.remove('btn-outline-custom');

                const filterValue = btn.getAttribute('data-filter');
                let visibleCount = 0;

                projectItems.forEach(item => {
                    const category = item.getAttribute('data-category');
                    if (filterValue === 'all' || category === filterValue) {
                        item.style.display = 'block';
                        visibleCount++;
                    } else {
                        item.style.display = 'none';
                    }
                });

                if (noProjectsMessage) {
                    noProjectsMessage.style.display = visibleCount === 0 ? 'block' : 'none';
                }
            });
        });
    }

    // 2. Blog Category Filter & Search
    const blogFilterButtons = document.querySelectorAll('.blog-filter-btn');
    const blogItems = document.querySelectorAll('.blog-item');
    const blogSearchInput = document.getElementById('blogSearchInput');
    const noBlogsMessage = document.getElementById('noBlogsMessage');

    function applyBlogFilters() {
        if (!blogItems.length) return;
        const activeBtn = document.querySelector('.blog-filter-btn.active');
        const activeCategory = activeBtn ? activeBtn.getAttribute('data-category') : 'all';
        const searchQuery = blogSearchInput ? blogSearchInput.value.toLowerCase().trim() : '';

        let visibleCount = 0;

        blogItems.forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            const title = item.querySelector('.blog-title')?.textContent.toLowerCase() || '';
            const excerpt = item.querySelector('.blog-excerpt')?.textContent.toLowerCase() || '';

            const matchesCategory = activeCategory === 'all' || itemCategory === activeCategory;
            const matchesSearch = !searchQuery || title.includes(searchQuery) || excerpt.includes(searchQuery);

            if (matchesCategory && matchesSearch) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        if (noBlogsMessage) {
            noBlogsMessage.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (blogFilterButtons.length > 0) {
        blogFilterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                blogFilterButtons.forEach(b => b.classList.remove('active', 'btn-primary-custom'));
                blogFilterButtons.forEach(b => b.classList.add('btn-outline-custom'));
                btn.classList.add('active', 'btn-primary-custom');
                btn.classList.remove('btn-outline-custom');
                applyBlogFilters();
            });
        });
    }

    if (blogSearchInput) {
        blogSearchInput.addEventListener('input', applyBlogFilters);
    }
});
