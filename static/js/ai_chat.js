/**
 * BUILD+ AI CUSTOMER CONSULTANT - CLIENT CONTROLLER v4.0
 * Enterprise conversational AI widget with instant qualification, quick actions,
 * interactive lead forms, zero raw emojis, and 100% Bootstrap Icons.
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'build_ai_session_id';
    let currentSessionId = localStorage.getItem(STORAGE_KEY) || '';
    let isChatOpen = false;
    let extractedData = {};

    // HTML Template for Floating Widget
    const widgetHTML = `
    <!-- FLOATING AI TRIGGER BUTTON -->
    <div id="aiFloatingTrigger" class="ai-floating-trigger" role="button" aria-label="Open AI Assistant" tabindex="0">
        <div class="bot-avatar">
            <i class="bi bi-robot"></i>
        </div>
        <span class="fw-bold small">AI Assistant</span>
        <span class="pulse-dot"></span>
    </div>

    <!-- AI CHAT WINDOW -->
    <div id="aiChatWindow" class="ai-chat-window" role="dialog" aria-hidden="true" aria-label="BUILD+ AI Consultant">
        <!-- Header -->
        <div class="ai-chat-header">
            <div class="header-brand">
                <div class="bot-icon-circle">
                    <i class="bi bi-robot"></i>
                </div>
                <div>
                    <div class="fw-bold small" id="aiBotName">BUILD+ AI Consultant</div>
                    <div class="status-line">
                        <span class="pulse-dot"></span> Online • Instant Consult
                    </div>
                </div>
            </div>
            <div class="header-controls">
                <button type="button" id="aiResetBtn" title="Restart Conversation" aria-label="Restart Conversation">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
                <button type="button" id="aiCloseBtn" title="Close Chat" aria-label="Close Chat">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        </div>

        <!-- Message Stream -->
        <div class="ai-chat-messages" id="aiMessageStream" role="log" aria-live="polite">
            <!-- Messages inserted dynamically -->
        </div>

        <!-- Typing Indicator -->
        <div class="ai-typing-indicator" id="aiTypingIndicator" aria-hidden="true">
            <small class="text-muted me-2 font-monospace">AI is thinking</small>
            <div class="ai-typing-dot"></div>
            <div class="ai-typing-dot"></div>
            <div class="ai-typing-dot"></div>
        </div>

        <!-- Footer Input -->
        <div class="ai-chat-footer">
            <form id="aiChatForm" class="m-0">
                <div class="ai-input-wrapper">
                    <input type="text" id="aiChatInput" class="ai-chat-input" placeholder="Ask about renovation, construction, demolition..." autocomplete="off" aria-label="Your message">
                    <button type="submit" id="aiSendBtn" class="ai-send-btn" aria-label="Send Message" title="Send Message">
                        <i class="bi bi-send-fill"></i>
                    </button>
                </div>
            </form>
        </div>
    </div>
    `;

    function initWidget() {
        // Avoid duplicate mounting
        if (document.getElementById('aiFloatingTrigger')) {
            return;
        }

        const mount = document.getElementById('buildAiAssistantMount');
        const container = mount || document.createElement('div');
        if (!mount) {
            container.id = 'buildAiAssistantMount';
            document.body.appendChild(container);
        }
        container.innerHTML = widgetHTML;

        const trigger = document.getElementById('aiFloatingTrigger');
        const closeBtn = document.getElementById('aiCloseBtn');
        const resetBtn = document.getElementById('aiResetBtn');
        const form = document.getElementById('aiChatForm');
        const input = document.getElementById('aiChatInput');

        if (trigger) {
            trigger.addEventListener('click', toggleChat);
            trigger.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleChat();
                }
            });
        }

        if (closeBtn) closeBtn.addEventListener('click', closeChat);
        if (resetBtn) resetBtn.addEventListener('click', resetConversation);

        if (form && input) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                const text = input.value.trim();
                if (text) {
                    input.value = '';
                    handleUserMessage(text);
                }
            });
        }

        // Close on ESC
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isChatOpen) {
                closeChat();
            }
        });

        // Also bind any page links with [data-open-ai-chat] or #aiChatToggle
        document.querySelectorAll('[data-open-ai-chat], #aiChatToggle').forEach(el => {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                openChat();
            });
        });

        // Initialize Chat session with Backend
        loadSession();
    }

    function openChat() {
        const windowEl = document.getElementById('aiChatWindow');
        if (!windowEl) return;
        isChatOpen = true;
        windowEl.classList.add('open');
        windowEl.setAttribute('aria-hidden', 'false');
        setTimeout(() => {
            const input = document.getElementById('aiChatInput');
            if (input) input.focus();
            scrollToBottom();
        }, 150);
    }

    function closeChat() {
        const windowEl = document.getElementById('aiChatWindow');
        if (!windowEl) return;
        isChatOpen = false;
        windowEl.classList.remove('open');
        windowEl.setAttribute('aria-hidden', 'true');
    }

    function toggleChat() {
        if (isChatOpen) {
            closeChat();
        } else {
            openChat();
        }
    }

    function resetConversation() {
        if (confirm('Start a new AI consultation session?')) {
            localStorage.removeItem(STORAGE_KEY);
            currentSessionId = '';
            extractedData = {};
            const stream = document.getElementById('aiMessageStream');
            if (stream) stream.innerHTML = '';
            loadSession();
        }
    }

    function scrollToBottom() {
        const stream = document.getElementById('aiMessageStream');
        if (stream) {
            setTimeout(() => {
                stream.scrollTop = stream.scrollHeight;
            }, 60);
        }
    }

    function loadSession() {
        fetch(`/api/ai/init/?session_id=${encodeURIComponent(currentSessionId)}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    currentSessionId = data.session_id;
                    localStorage.setItem(STORAGE_KEY, currentSessionId);

                    const botNameEl = document.getElementById('aiBotName');
                    if (botNameEl && data.ai_name) {
                        botNameEl.textContent = data.ai_name;
                    }
                    if (data.extracted_data) {
                        extractedData = data.extracted_data;
                    }

                    const stream = document.getElementById('aiMessageStream');
                    if (stream) {
                        stream.innerHTML = '';
                        if (data.messages && data.messages.length > 0) {
                            data.messages.forEach(msg => {
                                renderMessage(msg.sender, msg.content, msg.quick_actions, msg.created_at, msg.sender_name);
                            });
                        }
                        scrollToBottom();
                    }
                }
            })
            .catch(err => {
                console.error('AI Init Error:', err);
            });
    }

    function handleUserMessage(text) {
        renderMessage('user', text, [], new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        showTyping(true);
        scrollToBottom();

        fetch('/api/ai/message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: text
            })
        })
            .then(res => res.json())
            .then(data => {
                showTyping(false);
                if (data.status === 'ok' && data.reply) {
                    renderMessage(
                        data.reply.sender,
                        data.reply.content,
                        data.reply.quick_actions,
                        data.reply.created_at,
                        data.reply.sender_name
                    );
                    if (data.extracted_data) {
                        extractedData = Object.assign(extractedData, data.extracted_data);
                    }
                    scrollToBottom();
                } else if (data.status === 'human_active') {
                    renderMessage('bot', data.message, data.quick_actions, new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                } else {
                    renderMessage('bot', "Thank you for your enquiry. Our engineering desk will connect with you.", [
                        { label: "Request Free Site Inspection", action: "request_site_visit", type: "trigger" },
                        { label: "Call Us: +91 98765 43210", action: "tel:+919876543210", type: "link" }
                    ]);
                }
            })
            .catch(err => {
                showTyping(false);
                renderMessage('bot', "I apologize, I am temporarily having trouble connecting to the network. Please feel free to call our direct engineering desk at +91 98765 43210 or message on WhatsApp.", [
                    { label: "Call +91 98765 43210", action: "tel:+919876543210", type: "link" },
                    { label: "WhatsApp Chat", action: "https://wa.me/919876543210", type: "link" }
                ]);
            });
    }

    function formatContent(text) {
        if (!text) return '';
        // Escape HTML
        let escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Preserve basic bold markdown **text**
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Preserve newlines
        return escaped.replace(/\n/g, '<br>');
    }

    function renderMessage(sender, content, quickActions, timeStr, senderName) {
        const stream = document.getElementById('aiMessageStream');
        if (!stream) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-msg ${sender === 'user' ? 'user' : 'bot'}`;

        const bubbleContent = formatContent(content);

        let html = `
            <div class="ai-bubble">
                ${bubbleContent}
            </div>
            <div class="ai-bubble-meta">
                <span>${senderName || (sender === 'user' ? 'You' : 'BUILD+ AI')}</span> • <span>${timeStr || ''}</span>
            </div>
        `;

        msgDiv.innerHTML = html;

        // Render Quick Action Pills
        if (quickActions && quickActions.length > 0) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-quick-actions';

            quickActions.forEach(action => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'ai-pill-btn';

                // Add icon based on action type
                let iconHtml = '<i class="bi bi-chevron-right small me-1"></i>';
                if (action.type === 'link') {
                    if (action.action.startsWith('tel:')) iconHtml = '<i class="bi bi-telephone-fill me-1"></i>';
                    else if (action.action.includes('wa.me')) iconHtml = '<i class="bi bi-whatsapp me-1"></i>';
                    else iconHtml = '<i class="bi bi-box-arrow-up-right me-1"></i>';
                } else if (action.action === 'request_site_visit') {
                    iconHtml = '<i class="bi bi-geo-alt-fill me-1"></i>';
                } else if (action.action === 'request_summary' || action.action === 'request_estimate') {
                    iconHtml = '<i class="bi bi-clipboard-check-fill me-1"></i>';
                }

                btn.innerHTML = `${iconHtml}${action.label}`;

                btn.addEventListener('click', function () {
                    handleQuickAction(action);
                });

                actionsDiv.appendChild(btn);
            });

            msgDiv.appendChild(actionsDiv);
        }

        stream.appendChild(msgDiv);
        scrollToBottom();
    }

    function handleQuickAction(action) {
        if (action.action && action.action.startsWith('send_msg:')) {
            const msg = action.action.replace('send_msg:', '');
            handleUserMessage(msg);
        } else if (action.action === 'request_site_visit') {
            renderSiteVisitForm();
        } else if (action.action === 'request_summary' || action.action === 'request_estimate') {
            renderLeadSummaryForm();
        } else if (action.type === 'link') {
            window.open(action.action, '_blank');
        }
    }

    function renderSiteVisitForm() {
        const stream = document.getElementById('aiMessageStream');
        if (!stream) return;

        const card = document.createElement('div');
        card.className = 'ai-summary-card';
        card.innerHTML = `
            <div class="ai-summary-title">
                <span><i class="bi bi-geo-alt-fill text-warning me-1"></i> Schedule Free Site Inspection</span>
                <span class="badge bg-warning text-dark">Chartered Engineer</span>
            </div>
            <p class="small text-muted mb-2">Share your details to book a physical on-site structural audit & measurement visit.</p>
            <form id="aiSiteVisitForm" class="small">
                <div class="mb-2">
                    <input type="text" id="aiSvName" class="form-control form-control-sm" placeholder="Your Full Name" value="${extractedData.name || ''}" required>
                </div>
                <div class="mb-2">
                    <input type="tel" id="aiSvPhone" class="form-control form-control-sm" placeholder="Phone Number (e.g. +91 98888 77777)" value="${extractedData.phone || ''}" required>
                </div>
                <div class="mb-2">
                    <input type="text" id="aiSvLocation" class="form-control form-control-sm" placeholder="Property Location / City" value="${extractedData.location || ''}" required>
                </div>
                <div class="mb-2">
                    <input type="text" id="aiSvArea" class="form-control form-control-sm" placeholder="Approx Area (e.g. 1500 sq.ft, 3BHK)" value="${extractedData.area || ''}">
                </div>
                <button type="submit" class="btn btn-warning btn-sm w-100 fw-bold text-dark">
                    <i class="bi bi-calendar-check me-1"></i> Confirm Site Inspection Request
                </button>
            </form>
        `;

        stream.appendChild(card);
        scrollToBottom();

        const svForm = document.getElementById('aiSiteVisitForm');
        if (svForm) {
            svForm.addEventListener('submit', function (e) {
                e.preventDefault();
                const payload = {
                    session_id: currentSessionId,
                    name: document.getElementById('aiSvName').value,
                    phone: document.getElementById('aiSvPhone').value,
                    location: document.getElementById('aiSvLocation').value,
                    approximate_area: document.getElementById('aiSvArea').value,
                    site_visit_requested: true,
                };
                submitLeadToCRM(payload, card);
            });
        }
    }

    function renderLeadSummaryForm() {
        const stream = document.getElementById('aiMessageStream');
        if (!stream) return;

        const card = document.createElement('div');
        card.className = 'ai-summary-card';
        card.innerHTML = `
            <div class="ai-summary-title">
                <span><i class="bi bi-clipboard-data-fill text-primary me-1"></i> Project Scope & Estimate</span>
                <span class="badge bg-primary">BUILD+ Direct</span>
            </div>
            <form id="aiLeadForm" class="small">
                <div class="mb-2">
                    <input type="text" id="aiLeadName" class="form-control form-control-sm" placeholder="Your Full Name" value="${extractedData.name || ''}" required>
                </div>
                <div class="mb-2">
                    <input type="tel" id="aiLeadPhone" class="form-control form-control-sm" placeholder="Phone Number" value="${extractedData.phone || ''}" required>
                </div>
                <div class="mb-2">
                    <input type="text" id="aiLeadLocation" class="form-control form-control-sm" placeholder="City & Area" value="${extractedData.location || ''}">
                </div>
                <div class="mb-2">
                    <select id="aiLeadBudget" class="form-select form-select-sm">
                        <option value="">Select Estimated Budget Range</option>
                        <option value="Under ₹5 Lakhs">Under ₹5 Lakhs</option>
                        <option value="₹5–10 Lakhs">₹5–10 Lakhs</option>
                        <option value="₹10–25 Lakhs">₹10–25 Lakhs</option>
                        <option value="₹25–50 Lakhs">₹25–50 Lakhs</option>
                        <option value="₹50 Lakhs–1 Crore">₹50 Lakhs–1 Crore</option>
                        <option value="₹1 Crore+">₹1 Crore+</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary btn-sm w-100 fw-bold">
                    <i class="bi bi-check2-circle me-1"></i> Submit Details for Estimate
                </button>
            </form>
        `;

        stream.appendChild(card);
        scrollToBottom();

        const leadForm = document.getElementById('aiLeadForm');
        if (leadForm) {
            leadForm.addEventListener('submit', function (e) {
                e.preventDefault();
                const payload = {
                    session_id: currentSessionId,
                    name: document.getElementById('aiLeadName').value,
                    phone: document.getElementById('aiLeadPhone').value,
                    location: document.getElementById('aiLeadLocation').value,
                    budget: document.getElementById('aiLeadBudget').value,
                    site_visit_requested: false,
                };
                submitLeadToCRM(payload, card);
            });
        }
    }

    function submitLeadToCRM(payload, cardElement) {
        cardElement.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
                <small class="text-muted d-block">Registering in BUILD+ CRM...</small>
            </div>
        `;

        fetch('/api/ai/lead-capture/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    cardElement.innerHTML = `
                        <div class="text-center py-3">
                            <div class="h4 text-success mb-1"><i class="bi bi-check-circle-fill"></i> Registered!</div>
                            <div class="fw-bold text-dark font-monospace mb-1">Ref: ${data.lead_id}</div>
                            <small class="text-muted">Our senior engineering desk will review your details and reach out shortly.</small>
                        </div>
                    `;
                } else {
                    cardElement.innerHTML = `<div class="text-danger small py-2">Could not register details. Please call +91 98765 43210.</div>`;
                }
            })
            .catch(err => {
                cardElement.innerHTML = `<div class="text-danger small py-2">Submission error. Please call +91 98765 43210 directly.</div>`;
            });
    }

    function showTyping(show) {
        const indicator = document.getElementById('aiTypingIndicator');
        if (!indicator) return;
        if (show) {
            indicator.classList.add('active');
        } else {
            indicator.classList.remove('active');
        }
    }

    // Auto-mount on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
})();
