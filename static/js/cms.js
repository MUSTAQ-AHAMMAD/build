/**
 * BUILD+ Construction Portal & CMS JavaScript Utilities (Minimal Vanilla JS)
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-Slug Generator
    const titleInput = document.getElementById('id_title') || document.getElementById('id_cat_name');
    const slugInput = document.getElementById('id_slug') || document.getElementById('id_cat_slug');

    if (titleInput && slugInput) {
        titleInput.addEventListener('input', function () {
            // Only auto-update if slug hasn't been manually edited or is empty
            if (!slugInput.dataset.manualEdit) {
                const slugValue = titleInput.value
                    .toLowerCase()
                    .trim()
                    .replace(/[^\w\s-]/g, '')
                    .replace(/[\s_-]+/g, '-')
                    .replace(/^-+|-+$/g, '');
                slugInput.value = slugValue;
            }
        });

        slugInput.addEventListener('input', function () {
            slugInput.dataset.manualEdit = "true";
        });
    }

    // 2. Featured Image Upload Preview
    const imageInput = document.getElementById('id_featured_image');
    const imagePreviewContainer = document.getElementById('image-preview-box');

    if (imageInput && imagePreviewContainer) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    imagePreviewContainer.innerHTML = `
                        <div class="mt-2 border p-2 rounded bg-light text-center">
                            <small class="text-muted d-block mb-1">New Image Selected Preview:</small>
                            <img src="${event.target.result}" class="img-fluid rounded" style="max-height: 200px; object-fit: cover;">
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 3. AI Content Assistant AJAX Integration
    const aiSubmitBtn = document.getElementById('ai-generate-btn');
    if (aiSubmitBtn) {
        aiSubmitBtn.addEventListener('click', function () {
            const topicInput = document.getElementById('ai_topic');
            const taskSelect = document.getElementById('ai_task_type');
            const instructionsInput = document.getElementById('ai_instructions');
            const aiStatusBox = document.getElementById('ai-status-msg');
            const topic = topicInput ? topicInput.value.trim() : '';

            if (!topic) {
                if (aiStatusBox) {
                    aiStatusBox.innerHTML = '<div class="alert alert-warning py-2 mb-0">Please enter a topic before generating.</div>';
                }
                return;
            }

            aiSubmitBtn.disabled = true;
            aiSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Generating with Gemini AI...';
            if (aiStatusBox) {
                aiStatusBox.innerHTML = '<div class="alert alert-info py-2 mb-0">Connecting to Google AI Studio / Gemini Assistant...</div>';
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

            const formData = new FormData();
            formData.append('topic', topic);
            formData.append('task_type', taskSelect ? taskSelect.value : 'generate_draft');
            formData.append('custom_instructions', instructionsInput ? instructionsInput.value : '');

            fetch('/cms/blog/ai-assist/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                aiSubmitBtn.disabled = false;
                aiSubmitBtn.innerHTML = '✨ Generate Content';

                if (data.success) {
                    if (aiStatusBox) {
                        aiStatusBox.innerHTML = `<div class="alert alert-success py-2 mb-0">Success! Content generated from ${data.source}.</div>`;
                    }

                    // Populate fields in blog form
                    const contentField = document.getElementById('id_content');
                    const seoTitleField = document.getElementById('id_seo_title') || document.querySelector('[name=seo_title]');
                    const seoDescField = document.getElementById('id_seo_description') || document.querySelector('[name=seo_description]');
                    const seoKwField = document.getElementById('id_seo_keywords') || document.querySelector('[name=seo_keywords]');
                    const titleField = document.getElementById('id_title');

                    if (data.content && contentField) {
                        contentField.value = data.content;
                    }
                    if (data.seo_title && seoTitleField) {
                        seoTitleField.value = data.seo_title;
                    }
                    if (data.seo_description && seoDescField) {
                        seoDescField.value = data.seo_description;
                    }
                    if (data.seo_keywords && seoKwField) {
                        seoKwField.value = data.seo_keywords;
                    }
                    if (!titleField.value && topic) {
                        titleField.value = topic;
                        titleField.dispatchEvent(new Event('input'));
                    }
                } else {
                    if (aiStatusBox) {
                        aiStatusBox.innerHTML = `<div class="alert alert-danger py-2 mb-0">Error: ${data.error || 'Failed to generate content.'}</div>`;
                    }
                }
            })
            .catch(err => {
                aiSubmitBtn.disabled = false;
                aiSubmitBtn.innerHTML = '✨ Generate Content';
                if (aiStatusBox) {
                    aiStatusBox.innerHTML = '<div class="alert alert-danger py-2 mb-0">Request failed. Please check network connection.</div>';
                }
            });
        });
    }

    // 4. Interactive Cost Estimator & Budget Calculator
    const calcService = document.getElementById('calc_service');
    const calcArea = document.getElementById('calc_area');
    const areaBadge = document.getElementById('area_badge');
    const totalDisplay = document.getElementById('calc_total_display');
    const rateDisplay = document.getElementById('calc_rate_display');
    const breakdownCivil = document.getElementById('breakdown_civil');
    const breakdownMep = document.getElementById('breakdown_mep');
    const breakdownFinishes = document.getElementById('breakdown_finishes');

    function updateEstimator() {
        if (!calcService || !calcArea || !totalDisplay) return;

        const area = parseInt(calcArea.value, 10);
        if (areaBadge) areaBadge.textContent = area.toLocaleString() + ' sq.ft';

        const selectedOption = calcService.options[calcService.selectedIndex];
        const tierRadio = document.querySelector('input[name="calc_tier"]:checked');
        const tier = tierRadio ? tierRadio.value : 'prem';

        let rate = 2000;
        if (tier === 'base') {
            rate = parseInt(selectedOption.dataset.base || '1400', 10);
        } else if (tier === 'lux') {
            rate = parseInt(selectedOption.dataset.lux || '2600', 10);
        } else {
            rate = parseInt(selectedOption.dataset.prem || '2000', 10);
        }

        const totalCost = area * rate;
        const totalLakhs = (totalCost / 100000).toFixed(2);

        const civilCost = ((totalCost * 0.35) / 100000).toFixed(2);
        const mepCost = ((totalCost * 0.25) / 100000).toFixed(2);
        const finishesCost = ((totalCost * 0.40) / 100000).toFixed(2);

        totalDisplay.textContent = '₹ ' + totalLakhs + ' Lakhs';
        if (rateDisplay) {
            rateDisplay.textContent = 'Approx. ₹ ' + rate.toLocaleString() + ' / sq.ft (inclusive of materials, labor & supervision)';
        }
        if (breakdownCivil) breakdownCivil.textContent = '₹ ' + civilCost + ' L';
        if (breakdownMep) breakdownMep.textContent = '₹ ' + mepCost + ' L';
        if (breakdownFinishes) breakdownFinishes.textContent = '₹ ' + finishesCost + ' L';
    }

    if (calcService && calcArea) {
        calcService.addEventListener('change', updateEstimator);
        calcArea.addEventListener('input', updateEstimator);
        document.querySelectorAll('input[name="calc_tier"]').forEach(function (radio) {
            radio.addEventListener('change', updateEstimator);
        });
        updateEstimator();
    }
});

// Helper for CMS Rich Text Toolbar tag insertion
window.insertTag = function(elementId, openTag, closeTag) {
    const textarea = document.getElementById(elementId);
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const replacement = openTag + selectedText + closeTag;

    textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    textarea.focus();
    textarea.setSelectionRange(start + openTag.length, start + openTag.length + selectedText.length);
};
