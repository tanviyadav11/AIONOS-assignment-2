/**
 * Veridian Corp IT Support Agent - Frontend Application Logic
 * Implements Theme Switching, Staggered Pipeline Animations, Interactive Popover Chips,
 * Typing Indicator Clarifications, and Ticket Filtering.
 */

let allRequests = [];
let allKnowledgeBase = [];
let allPrecedents = [];
let activeRequestId = null;
let currentReasoning = null;
let currentTicket = null;

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    loadSeedRequests();
    loadKnowledgeBase();
    loadPrecedents();
    loadTicketQueue();
    setupEventListeners();
});

// --------------------------------------------------------------------------
// 1. Theme Switcher (Light / Dark Mode)
// --------------------------------------------------------------------------
function initTheme() {
    const savedTheme = localStorage.getItem('veridian-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme ? savedTheme : (prefersDark ? 'dark' : 'light');

    setTheme(initialTheme);

    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(nextTheme);
        });
    }

    // Listen for OS theme changes if user hasn't explicitly set a preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('veridian-theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('veridian-theme', theme);
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.innerText = theme === 'dark' ? '☀️' : '🌙';
    }
}

// --------------------------------------------------------------------------
// 2. Tab Navigation
// --------------------------------------------------------------------------
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            const targetEl = document.getElementById(target);
            if (targetEl) {
                targetEl.classList.add('active');
            }

            if (target === 'queue-tab') {
                loadTicketQueue();
            } else if (target === 'kb-tab') {
                loadKnowledgeBase();
            }
        });
    });
}

// --------------------------------------------------------------------------
// 3. Request Loader & Selection
// --------------------------------------------------------------------------
async function loadSeedRequests() {
    try {
        const res = await fetch('/api/requests');
        allRequests = await res.json();
        renderRequestCards(allRequests);
        
        // Auto-select REQ-01 by default on load
        if (allRequests.length > 0) {
            selectRequest(allRequests[0].id);
        }
    } catch (err) {
        console.error("Failed to load requests:", err);
    }
}

function renderRequestCards(requests) {
    const container = document.getElementById('req-cards-container');
    if (!container) return;
    container.innerHTML = '';

    requests.forEach(req => {
        const card = document.createElement('div');
        card.className = `req-card ${activeRequestId === req.id ? 'active' : ''}`;
        card.id = `card-${req.id}`;
        card.onclick = () => selectRequest(req.id);

        let statusBadge = req.status_so_far;
        let badgeColor = 'var(--color-text-muted)';
        if (req.status_so_far.includes('Waiting')) badgeColor = 'var(--color-info)';
        else if (req.status_so_far.includes('Investigating')) badgeColor = 'var(--color-inst)';
        else if (req.status_so_far.includes('Escalated')) badgeColor = 'var(--color-danger)';
        else if (req.status_so_far.includes('progress') || req.status_so_far.includes('Pending')) badgeColor = 'var(--color-warning)';

        card.innerHTML = `
            <div class="req-card-top">
                <span class="req-id">${req.id}</span>
                <span class="req-employee">${req.employee}</span>
            </div>
            <div class="req-text">"${req.request}"</div>
            <div class="req-card-footer">
                <span style="color: var(--color-text-muted); font-size: 0.7rem;">${req.date}</span>
                <span class="req-status-tag" style="color: ${badgeColor}; border: 1px solid ${badgeColor}33;">${statusBadge}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function selectRequest(reqId) {
    activeRequestId = reqId;
    document.querySelectorAll('.req-card').forEach(c => c.classList.remove('active'));
    const selectedEl = document.getElementById(`card-${reqId}`);
    if (selectedEl) selectedEl.classList.add('active');

    const req = allRequests.find(r => r.id === reqId);
    if (!req) return;

    document.getElementById('input-employee').value = req.employee;
    document.getElementById('input-email').value = req.email;
    document.getElementById('input-text').value = req.request;
    document.getElementById('current-req-id-badge').innerText = req.id;

    // Reset follow-up box
    document.getElementById('followup-drawer').style.display = 'none';

    // Process request to demonstrate live agentic pipeline
    processCurrentRequest();
}

// --------------------------------------------------------------------------
// 4. Request Processing Pipeline & Animations
// --------------------------------------------------------------------------
async function processCurrentRequest(followUpAnswer = null) {
    const text = document.getElementById('input-text').value.trim();
    const employee = document.getElementById('input-employee').value.trim();
    const email = document.getElementById('input-email').value.trim();
    const runBtn = document.getElementById('run-btn');

    if (!text) return;

    // Set loading state
    runBtn.innerHTML = `<div class="spinner"></div> Processing...`;
    runBtn.disabled = true;

    try {
        const payload = {
            text: text,
            employee_name: employee,
            employee_email: email,
            request_id: activeRequestId,
            follow_up_answer: followUpAnswer,
            interactive: true
        };

        const res = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        currentReasoning = data.reasoning;
        currentTicket = data.ticket;

        renderReasoningOutput(data);
    } catch (err) {
        console.error("Error evaluating request:", err);
        alert("Failed to process request. Check server console.");
    } finally {
        runBtn.innerHTML = `<span>⚡</span> Evaluate & Resolve`;
        runBtn.disabled = false;
    }
}

function renderReasoningOutput(data) {
    const r = data.reasoning;
    const t = data.ticket;

    // 1. Pipeline Steps with Sequential Stagger Animation
    const stepBoxes = document.querySelectorAll('.pipeline-steps .step-box');
    stepBoxes.forEach((box, i) => {
        box.classList.remove('animate-in');
        void box.offsetWidth; // Force reflow to replay CSS keyframes
        box.classList.add('animate-in');
    });

    document.getElementById('step1-desc').innerText = `${r.category} (${(r.confidence * 100).toFixed(0)}%)`;
    document.getElementById('step2-desc').innerText = `${r.matched_kb_ids.join(', ') || 'None'}`;
    document.getElementById('step3-desc').innerText = `${r.decision.replace(/_/g, ' ')}`;
    document.getElementById('step4-desc').innerText = `${t ? t.ticket_id : 'Completed'}`;

    // 2. Policy Conflict Banner (KB-03 vs Asset Management Policy)
    const conflictBox = document.getElementById('conflict-alert-box');
    if (r.policy_conflict_detected) {
        conflictBox.style.display = 'flex';
        document.getElementById('conflict-summary-text').innerText = r.policy_conflict_summary;
    } else {
        conflictBox.style.display = 'none';
    }

    // 3. Security Violation Banner (KB-09 Forwarding)
    const secBox = document.getElementById('security-alert-box');
    if (r.security_violation_flag) {
        secBox.style.display = 'flex';
        document.getElementById('security-details-text').innerText = r.security_violation_details;
    } else {
        secBox.style.display = 'none';
    }

    // 4. Decision & Ticket Metadata
    document.getElementById('ticket-id-val').innerText = t ? t.ticket_id : 'N/A';
    document.getElementById('ticket-status-val').innerText = t ? t.status : r.decision.replace(/_/g, ' ');
    
    const badgeEl = document.getElementById('decision-badge-val');
    badgeEl.className = `decision-badge ${r.decision}`;
    
    // Status Icon + Label mapping
    let icon = 'ℹ️';
    let label = r.decision.replace(/_/g, ' ');
    if (r.decision === 'AUTO_RESOLVED') {
        icon = '✓';
        label = 'AUTO RESOLVED';
    } else if (r.decision === 'RESOLVED_WITH_INSTRUCTIONS') {
        icon = '📋';
        label = 'INSTRUCTIONS PROVIDED';
    } else if (r.decision === 'PENDING_APPROVAL') {
        icon = '⏳';
        label = 'PENDING APPROVAL';
    } else if (r.decision === 'ESCALATED_SECURITY') {
        icon = '🚨';
        label = 'ESCALATED (SECURITY)';
    } else if (r.decision === 'NEEDS_CLARIFICATION') {
        icon = '❓';
        label = 'NEEDS CLARIFICATION';
    }
    badgeEl.innerHTML = `<span class="badge-icon">${icon}</span> <span class="badge-text">${label}</span>`;

    document.getElementById('category-val').innerText = r.category;
    document.getElementById('approver-val').innerText = r.approver_if_any || 'None required';
    document.getElementById('sla-val').innerText = r.sla_if_any || 'Not stated in policy';

    // 5. Follow-up Clarification Drawer with Typing Indicator
    const followupDrawer = document.getElementById('followup-drawer');
    const typingIndicator = document.getElementById('typing-indicator-box');
    const followupQText = document.getElementById('followup-q-text');
    const followupInputContainer = document.getElementById('followup-input-container');

    if (data.needs_follow_up) {
        followupDrawer.style.display = 'flex';
        
        // Show typing indicator briefly before revealing question
        typingIndicator.style.display = 'inline-flex';
        followupQText.style.display = 'none';
        followupInputContainer.style.display = 'none';

        setTimeout(() => {
            typingIndicator.style.display = 'none';
            followupQText.style.display = 'block';
            followupInputContainer.style.display = 'flex';
            followupQText.innerText = data.follow_up_question;

            // Auto-fill simulated answer if seed request has one
            const seedReq = allRequests.find(req => req.id === activeRequestId);
            if (seedReq && seedReq.simulated_follow_up_answer) {
                document.getElementById('followup-input').value = seedReq.simulated_follow_up_answer;
            } else {
                document.getElementById('followup-input').value = '';
            }
        }, 380);
    } else {
        followupDrawer.style.display = 'none';
    }

    // 6. Employee Response & Interactive Citations
    document.getElementById('response-text-content').innerText = r.employee_response_text;
    renderCitationChips(r.sources_cited);

    // 7. Audit Trail
    renderAuditTable(r.audit_trail);
}

function renderCitationChips(sources) {
    const citContainer = document.getElementById('citations-list');
    citContainer.innerHTML = '';

    (sources || []).forEach(cit => {
        const chip = document.createElement('button');
        chip.className = 'citation-chip';
        chip.type = 'button';
        chip.innerHTML = `<span>📖</span> <span>${cit}</span>`;
        
        // Add interactive popover on mouseenter / click
        chip.addEventListener('mouseenter', (e) => showCitationPopover(cit, e.target));
        chip.addEventListener('mouseleave', () => hideCitationPopover());
        chip.addEventListener('click', (e) => {
            e.stopPropagation();
            showCitationPopover(cit, e.target, true);
        });

        citContainer.appendChild(chip);
    });
}

function showCitationPopover(sourceId, targetEl, sticky = false) {
    const popover = document.getElementById('citation-popover');
    const popTitle = document.getElementById('popover-id');
    const popCat = document.getElementById('popover-category');
    const popText = document.getElementById('popover-text');
    const popApprovals = document.getElementById('popover-approvals');
    const popSla = document.getElementById('popover-sla');

    const cleanId = sourceId.trim().toUpperCase();
    
    // Check Knowledge Base
    const kb = allKnowledgeBase.find(k => k.kb_id === cleanId || cleanId.includes(k.kb_id));
    // Check Precedents
    const prec = allPrecedents.find(p => p.precedent_id === cleanId || cleanId.includes(p.precedent_id));

    if (kb) {
        popTitle.innerText = `${kb.kb_id}: ${kb.title}`;
        popCat.innerText = kb.category;
        popText.innerText = kb.full_text;
        popApprovals.innerText = kb.approvals_required || 'None';
        popSla.innerText = kb.sla || 'Not stated in policy';
    } else if (prec) {
        popTitle.innerText = `${prec.precedent_id} (${prec.category})`;
        popCat.innerText = `Precedent • ${prec.decision}`;
        popText.innerText = `Case: "${prec.request_summary}" → Resolution: ${prec.reasoning_summary}`;
        popApprovals.innerText = prec.approver || 'Standard';
        popSla.innerText = prec.stated_sla || 'Not stated';
    } else {
        popTitle.innerText = cleanId;
        popCat.innerText = 'Corporate Policy';
        popText.innerText = 'Veridian Corp official operational guideline referenced in this decision.';
        popApprovals.innerText = 'Standard IT Review';
        popSla.innerText = 'Not stated in policy';
    }

    const rect = targetEl.getBoundingClientRect();
    popover.style.top = `${Math.min(window.innerHeight - 220, rect.bottom + 6)}px`;
    popover.style.left = `${Math.max(10, Math.min(window.innerWidth - 350, rect.left))}px`;
    popover.style.display = 'flex';
}

function hideCitationPopover() {
    const popover = document.getElementById('citation-popover');
    if (popover) {
        popover.style.display = 'none';
    }
}

function renderAuditTable(auditTrail) {
    const tbody = document.getElementById('audit-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    (auditTrail || []).forEach(step => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--color-primary);">#${step.step_num}</td>
            <td style="font-weight: 600;">${step.step_name}</td>
            <td style="color: var(--color-text-secondary);">${step.input_summary}</td>
            <td style="color: var(--color-text); font-weight: 500;">${step.output_summary}</td>
            <td style="color: var(--color-text-muted); font-size: 0.725rem;">${step.rationale}</td>
        `;
        tbody.appendChild(row);
    });
}

function submitFollowUp() {
    const ans = document.getElementById('followup-input').value.trim();
    if (!ans) return;
    processCurrentRequest(ans);
}

// --------------------------------------------------------------------------
// 5. Ticket Queue Management
// --------------------------------------------------------------------------
async function loadTicketQueue() {
    const statusFilter = document.getElementById('status-filter') ? document.getElementById('status-filter').value : 'all';
    const categoryFilter = document.getElementById('category-filter') ? document.getElementById('category-filter').value : 'All';
    const searchVal = document.getElementById('search-input') ? document.getElementById('search-input').value.trim() : '';

    try {
        let url = `/api/tickets?status=${encodeURIComponent(statusFilter)}&category=${encodeURIComponent(categoryFilter)}`;
        if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;

        const res = await fetch(url);
        const tickets = await res.json();
        renderTicketQueueTable(tickets);
    } catch (err) {
        console.error("Error loading tickets:", err);
    }
}

function renderTicketQueueTable(tickets) {
    const tbody = document.getElementById('queue-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const countBadge = document.getElementById('queue-count-badge');
    if (countBadge) {
        countBadge.innerText = `${tickets.length} Tickets`;
    }

    tickets.forEach(t => {
        const tr = document.createElement('tr');
        tr.onclick = () => openTicketDetailModal(t);

        let badgeClass = t.decision;
        let icon = 'ℹ️';
        if (t.decision === 'AUTO_RESOLVED') icon = '✓';
        else if (t.decision === 'RESOLVED_WITH_INSTRUCTIONS') icon = '📋';
        else if (t.decision === 'PENDING_APPROVAL') icon = '⏳';
        else if (t.decision === 'ESCALATED_SECURITY') icon = '🚨';
        else if (t.decision === 'NEEDS_CLARIFICATION') icon = '❓';

        tr.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--color-primary);">
                ${t.ticket_id}
                ${t.is_precedent ? '<span class="precedent-tag">PRECEDENT</span>' : ''}
            </td>
            <td style="font-weight: 600;">${t.employee}</td>
            <td style="color: var(--color-text-secondary); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${t.original_request}
            </td>
            <td><span class="badge-tag">${t.category}</span></td>
            <td>
                <span class="decision-badge ${badgeClass}" style="font-size: 0.65rem; padding: 2px 7px;">
                    <span>${icon}</span> ${t.decision.replace(/_/g, ' ')}
                </span>
            </td>
            <td style="font-size: 0.78rem; color: ${t.status.includes('closed') ? 'var(--color-text-muted)' : 'var(--color-warning)'};">
                ${t.status}
            </td>
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.725rem; color: var(--color-primary);">
                ${t.kb_sources.join(', ') || 'N/A'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openTicketDetailModal(t) {
    document.getElementById('modal-ticket-id').innerText = `${t.ticket_id} — ${t.employee}`;
    document.getElementById('modal-request-text').innerText = `"${t.original_request}"`;
    document.getElementById('modal-category').innerText = t.category;
    
    const modalDec = document.getElementById('modal-decision');
    modalDec.innerText = t.decision.replace(/_/g, ' ');
    modalDec.className = `decision-badge ${t.decision}`;
    
    document.getElementById('modal-status').innerText = t.status;
    document.getElementById('modal-approver').innerText = t.approver_if_any || 'None';
    document.getElementById('modal-sla').innerText = t.sla_if_any || 'Not stated in policy';
    document.getElementById('modal-reasoning').innerText = t.reasoning_summary;
    document.getElementById('modal-sources').innerText = t.kb_sources.join(', ') || 'None';

    // Render audit steps in modal
    const modalAuditTbody = document.getElementById('modal-audit-tbody');
    modalAuditTbody.innerHTML = '';
    (t.audit_trail || []).forEach(step => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; color: var(--color-primary); font-weight: 700;">#${step.step_num}</td>
            <td style="font-weight: 600;">${step.step_name}</td>
            <td style="color: var(--color-text-secondary);">${step.input_summary}</td>
            <td>${step.output_summary}</td>
            <td style="color: var(--color-text-muted); font-size: 0.725rem;">${step.rationale}</td>
        `;
        modalAuditTbody.appendChild(row);
    });

    document.getElementById('ticket-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('ticket-modal').classList.remove('active');
}

// --------------------------------------------------------------------------
// 6. Knowledge Base & Precedents
// --------------------------------------------------------------------------
async function loadKnowledgeBase() {
    try {
        const res = await fetch('/api/knowledge-base');
        allKnowledgeBase = await res.json();
        renderKnowledgeBase(allKnowledgeBase);
    } catch (err) {
        console.error("Error loading KB:", err);
    }
}

async function loadPrecedents() {
    try {
        const res = await fetch('/api/precedents');
        allPrecedents = await res.json();
    } catch (err) {
        console.error("Error loading precedents:", err);
    }
}

function renderKnowledgeBase(articles) {
    const container = document.getElementById('kb-grid-container');
    if (!container) return;
    container.innerHTML = '';

    articles.forEach(kb => {
        const card = document.createElement('div');
        const isAssetPolicy = kb.kb_id === 'ASSET-POLICY';
        card.className = `kb-card ${isAssetPolicy ? 'special-policy' : ''}`;

        card.innerHTML = `
            <div class="kb-card-top">
                <span class="kb-id-badge" style="${isAssetPolicy ? 'background: var(--color-warning-bg); color: var(--color-warning);' : ''}">${kb.kb_id}</span>
                <span class="badge-tag">${kb.category}</span>
            </div>
            <h3 class="kb-title">${kb.title}</h3>
            <p class="kb-text">${kb.full_text}</p>
            <div class="kb-meta">
                <div><strong style="color: var(--color-text-muted);">Approvals:</strong> ${kb.approvals_required || 'None'}</div>
                <div><strong style="color: var(--color-text-muted);">Stated SLA:</strong> ${kb.sla || 'Not stated in policy'}</div>
                ${kb.special_notes ? `<div><strong style="color: var(--color-warning);">Note:</strong> ${kb.special_notes}</div>` : ''}
            </div>
        `;
        container.appendChild(card);
    });
}

// --------------------------------------------------------------------------
// 7. Event Listeners & Actions
// --------------------------------------------------------------------------
function setupEventListeners() {
    document.getElementById('run-btn').addEventListener('click', () => processCurrentRequest());
    document.getElementById('followup-submit-btn').addEventListener('click', submitFollowUp);

    // Audit toggle
    const toggleAuditBtn = document.getElementById('toggle-audit-btn');
    const auditTableWrapper = document.getElementById('audit-table-wrapper');
    if (toggleAuditBtn && auditTableWrapper) {
        toggleAuditBtn.addEventListener('click', () => {
            const isHidden = auditTableWrapper.style.display === 'none';
            auditTableWrapper.style.display = isHidden ? 'block' : 'none';
        });
    }

    // Dismiss popover on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.citation-chip') && !e.target.closest('.citation-popover')) {
            hideCitationPopover();
        }
    });

    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (confirm("Reset database to initial seed state (TK-1042..TK-1051)?")) {
                await fetch('/api/reset', { method: 'POST' });
                await loadSeedRequests();
                await loadTicketQueue();
                alert("Database reset to initial seed state.");
            }
        });
    }

    const runBatchBtn = document.getElementById('run-batch-btn');
    if (runBatchBtn) {
        runBatchBtn.addEventListener('click', async () => {
            runBatchBtn.disabled = true;
            runBatchBtn.innerText = "Running all 15...";
            for (const req of allRequests) {
                selectRequest(req.id);
                await processCurrentRequest();
                await new Promise(r => setTimeout(r, 180));
            }
            runBatchBtn.disabled = false;
            runBatchBtn.innerHTML = `<span>▶</span> Run All REQ-01..15`;
            alert("All 15 Data Pack requests processed and tickets recorded!");
        });
    }

    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) statusFilter.addEventListener('change', loadTicketQueue);

    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) categoryFilter.addEventListener('change', loadTicketQueue);

    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.addEventListener('input', loadTicketQueue);
}
