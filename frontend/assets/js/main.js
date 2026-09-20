/* ==============================================================================
   BUILD+ MAIN INTERACTIVITY (HEADER, BEFORE/AFTER SLIDER, STEPPER, SEARCH)
   ============================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Header Scroll Effect
    const header = document.querySelector('.site-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 40) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // 2. Interactive Before/After Comparison Sliders
    const baContainers = document.querySelectorAll('.ba-container');
    baContainers.forEach(container => {
        const overlay = container.querySelector('.ba-overlay');
        const handle = container.querySelector('.ba-handle');
        if (!overlay || !handle) return;

        let isDragging = false;

        const setPosition = (clientX) => {
            const rect = container.getBoundingClientRect();
            let offsetX = clientX - rect.left;
            if (offsetX < 0) offsetX = 0;
            if (offsetX > rect.width) offsetX = rect.width;

            const percentage = (offsetX / rect.width) * 100;
            overlay.style.width = `${percentage}%`;
            handle.style.left = `${percentage}%`;
        };

        const onMove = (e) => {
            if (!isDragging) return;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            setPosition(clientX);
        };

        const startDragging = (e) => {
            isDragging = true;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            setPosition(clientX);
        };

        const stopDragging = () => {
            isDragging = false;
        };

        container.addEventListener('mousedown', startDragging);
        container.addEventListener('touchstart', startDragging, { passive: true });
        window.addEventListener('mousemove', onMove);
        window.addEventListener('touchmove', onMove, { passive: true });
        window.addEventListener('mouseup', stopDragging);
        window.addEventListener('touchend', stopDragging);
    });

    // 3. Progressive 5-Step Enquiry Stepper Form
    const stepperForm = document.getElementById('progressiveEnquiryForm');
    if (stepperForm) {
        let currentStep = 1;
        const totalSteps = 5;

        const updateStepperUI = () => {
            // Update Step Contents
            for (let i = 1; i <= totalSteps; i++) {
                const stepPane = document.getElementById(`stepPane${i}`);
                const indicator = document.getElementById(`stepIndicator${i}`);
                if (stepPane) {
                    if (i === currentStep) {
                        stepPane.classList.add('active');
                    } else {
                        stepPane.classList.remove('active');
                    }
                }
                if (indicator) {
                    if (i === currentStep) {
                        indicator.classList.add('active');
                        indicator.classList.remove('completed');
                    } else if (i < currentStep) {
                        indicator.classList.add('completed');
                        indicator.classList.remove('active');
                    } else {
                        indicator.classList.remove('active', 'completed');
                    }
                }
            }
        };

        // Next Buttons
        document.querySelectorAll('.btn-next-step').forEach(btn => {
            btn.addEventListener('click', () => {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateStepperUI();
                }
            });
        });

        // Prev Buttons
        document.querySelectorAll('.btn-prev-step').forEach(btn => {
            btn.addEventListener('click', () => {
                if (currentStep > 1) {
                    currentStep--;
                    updateStepperUI();
                }
            });
        });

        // Form Submit Simulation
        stepperForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const successBox = document.getElementById('formSuccessMessage');
            if (successBox) {
                stepperForm.style.display = 'none';
                successBox.style.display = 'block';
            }
        });
    }

    // 4. Global Search Modal Filter
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('globalSearchResults');
    if (searchInput && searchResults) {
        const items = [
            { title: 'Independent House & Villa Construction', category: 'Construction', url: 'construction.html' },
            { title: 'Flat & Apartment Renovation (Old & Damaged)', category: 'Renovation', url: 'renovation.html' },
            { title: 'Structural Waterproofing & Polymer Mortar Repair', category: 'Renovation', url: 'renovation.html' },
            { title: 'Controlled Mechanical Building Demolition', category: 'Demolition', url: 'demolition-reconstruction.html' },
            { title: 'Housing Society Redevelopment Feasibility', category: 'Redevelopment', url: 'redevelopment.html' },
            { title: 'NRI Property Oversight & Drone Audits', category: 'NRI Services', url: 'nri-services.html' },
            { title: 'Land Valuation & Title Due Diligence', category: 'Property & Land', url: 'property-land.html' },
            { title: 'Construction Loan Documentation & Valuation', category: 'Finance', url: 'contact.html' },
        ];

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query) {
                searchResults.innerHTML = '<p class="text-muted small text-center my-3">Type to search services, projects, guides, or regulations...</p>';
                return;
            }

            const matched = items.filter(item => 
                item.title.toLowerCase().includes(query) || 
                item.category.toLowerCase().includes(query)
            );

            if (matched.length === 0) {
                searchResults.innerHTML = '<p class="text-muted small text-center my-3">No matching results found. Try another keyword.</p>';
                return;
            }

            let html = '<ul class="list-group list-group-flush">';
            matched.forEach(item => {
                html += `
                    <li class="list-group-item bg-transparent border-bottom py-2 d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge bg-secondary bg-opacity-25 text-body small me-2">${item.category}</span>
                            <a href="${item.url}" class="fw-semibold text-decoration-none">${item.title}</a>
                        </div>
                        <a href="${item.url}" class="btn btn-sm btn-outline-secondary py-0">View →</a>
                    </li>
                `;
            });
            html += '</ul>';
            searchResults.innerHTML = html;
        });
    }
});
