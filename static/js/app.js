/**
 * TALENT ENRICHMENT CLUB - CLIENT APPLICATION LOGIC
 * Real-time event registration, directory filtering, authentication & UI interactions
 */

// Global State
let currentEvents = [];
let currentMembers = [];
let activeCategoryFilter = 'All';
let currentUser = null; // { name, uid, email, department, role: 'student'|'admin' }

// Fallback seed data if running purely client-side without Flask
const SEED_EVENTS = [
    { id: 1, title: 'Cricket Championship', category: 'Sports', description: 'Annual inter-department T20 cricket tournament.', date: '2026-11-15', venue: 'Main Sports Ground', max_seats: 60 },
    { id: 2, title: 'Football League', category: 'Sports', description: '5-a-side high intensity football tournament.', date: '2026-11-18', venue: 'Turf Arena', max_seats: 40 },
    { id: 3, title: 'Badminton Masters', category: 'Sports', description: 'Singles and Doubles badminton open cup.', date: '2026-11-20', venue: 'Indoor Sports Complex', max_seats: 32 },
    { id: 4, title: 'Basketball Shootout', category: 'Sports', description: 'Inter-department basketball cup.', date: '2026-11-22', venue: 'Basketball Court', max_seats: 40 },
    { id: 5, title: 'Kabaddi Warriors', category: 'Sports', description: 'Traditional style kabaddi championship.', date: '2026-11-25', venue: 'Outdoor Arena', max_seats: 35 },
    { id: 6, title: 'Table Tennis Open', category: 'Sports', description: 'Fast-paced table tennis singles & doubles.', date: '2026-11-26', venue: 'Recreation Hall', max_seats: 24 },
    { id: 7, title: 'Vocal & Instrumental Music', category: 'Cultural', description: 'Solo and group singing and acoustic performances.', date: '2026-11-28', venue: 'Auditorium Hall A', max_seats: 50 },
    { id: 8, title: 'Choreography & Dance', category: 'Cultural', description: 'Classical, western, and freestyle dance showcase.', date: '2026-11-29', venue: 'Open Air Theatre', max_seats: 50 },
    { id: 9, title: 'Skits & Theatrical Drama', category: 'Cultural', description: 'Creative theatrical acts and satirical skits.', date: '2026-11-30', venue: 'Auditorium Hall B', max_seats: 40 },
    { id: 10, title: 'Standup Comedy Night', category: 'Cultural', description: 'Open-mic humorous performances and satire.', date: '2026-12-01', venue: 'Seminar Hall', max_seats: 30 },
    { id: 11, title: 'Canvas Oil & Watercolor Painting', category: 'Arts', description: 'Theme-based live painting competition.', date: '2026-12-03', venue: 'Art Studio 2', max_seats: 45 },
    { id: 12, title: 'Pencil Sketching & Caricature', category: 'Arts', description: 'Live portrait and landscape sketch challenge.', date: '2026-12-04', venue: 'Design Studio', max_seats: 45 },
    { id: 13, title: 'Digital Illustration & Design', category: 'Arts', description: 'Digital art contest using tablets and creative software.', date: '2026-12-05', venue: 'Computer Lab 3', max_seats: 35 }
];

const SEED_MEMBERS = [
    { id: 1, name: 'Alex Morgan', department: 'CSE', uid: 'UID202601', email: 'alex.m@example.com', event: 'Sports Event: Cricket Championship' },
    { id: 2, name: 'Sophia Chen', department: 'AIML', uid: 'UID202602', email: 'sophia.c@example.com', event: 'Cultural Event: Vocal & Instrumental Music' },
    { id: 3, name: 'Rahul Verma', department: 'DS', uid: 'UID202603', email: 'rahul.v@example.com', event: 'Arts Event: Canvas Oil & Watercolor Painting' },
    { id: 4, name: 'Emily Watson', department: 'BBA', uid: 'UID202604', email: 'emily.w@example.com', event: 'Sports Event: Badminton Masters' },
    { id: 5, name: 'David Miller', department: 'BCA', uid: 'UID202605', email: 'david.m@example.com', event: 'Cultural Event: Choreography & Dance' },
    { id: 6, name: 'Ananya Sharma', department: 'MCA', uid: 'UID202606', email: 'ananya.s@example.com', event: 'Arts Event: Pencil Sketching & Caricature' }
];

// Document Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initSession();
    fetchStats();
    loadEvents();
    loadMembers();
    initEventCategoryRadios();
    initForms();
});

/* ==========================================================================
   NAVIGATION & UI CONTROLS
   ========================================================================== */
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu.classList.contains('open')) {
                navMenu.classList.remove('open');
            }
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Modal Triggers
    const btnLoginModal = document.getElementById('btnLoginModal');
    const btnRegisterModal = document.getElementById('btnRegisterModal');
    const btnCloseAuthModal = document.getElementById('btnCloseAuthModal');
    const authModal = document.getElementById('authModal');

    if (btnLoginModal) btnLoginModal.addEventListener('click', () => openAuthModal('studentLogin'));
    if (btnRegisterModal) btnRegisterModal.addEventListener('click', () => openAuthModal('studentRegister'));
    if (btnCloseAuthModal) btnCloseAuthModal.addEventListener('click', closeAuthModal);

    // Close on backdrop click
    if (authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }

    const ticketModal = document.getElementById('ticketModal');
    const btnCloseTicketModal = document.getElementById('btnCloseTicketModal');
    if (btnCloseTicketModal) btnCloseTicketModal.addEventListener('click', closeTicketModal);
    if (ticketModal) {
        ticketModal.addEventListener('click', (e) => {
            if (e.target === ticketModal) closeTicketModal();
        });
    }

    // Modal Tabs
    const modalTabs = document.querySelectorAll('.modal-tab');
    modalTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchAuthTab(tab.dataset.tab);
        });
    });
}

function openAuthModal(defaultTab = 'studentLogin') {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.add('active');
        switchAuthTab(defaultTab);
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('active');
}

function closeTicketModal() {
    const modal = document.getElementById('ticketModal');
    if (modal) modal.classList.remove('active');
}

function switchAuthTab(tabName) {
    const tabs = document.querySelectorAll('.modal-tab');
    const panes = document.querySelectorAll('.auth-tab-pane');

    tabs.forEach(t => {
        if (t.dataset.tab === tabName) t.classList.add('active');
        else t.classList.remove('active');
    });

    panes.forEach(p => {
        if (p.id === 'pane' + tabName.charAt(0).toUpperCase() + tabName.slice(1)) {
            p.classList.add('active');
        } else {
            p.classList.remove('active');
        }
    });
}

/* ==========================================================================
   USER & ADMIN SESSION
   ========================================================================== */
function initSession() {
    const saved = localStorage.getItem('tec_user_session');
    if (saved) {
        try {
            currentUser = JSON.parse(saved);
            updateUserNavState();
        } catch (e) {
            currentUser = null;
        }
    }
}

function updateUserNavState() {
    const navActions = document.getElementById('navActions');
    const adminLockScreen = document.getElementById('adminLockScreen');
    const adminDashboardView = document.getElementById('adminDashboardView');
    const adminCols = document.querySelectorAll('.admin-only-col');
    const sessionStatusCard = document.getElementById('sessionStatusCard');

    if (!navActions) return;

    if (currentUser) {
        const isAdmin = currentUser.role === 'admin';
        navActions.innerHTML = `
            <div class="user-profile-badge">
                <div class="user-avatar-circle">${currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}</div>
                <span>${currentUser.name || currentUser.username}</span>
                ${isAdmin ? '<span class="badge badge-admin">Admin</span>' : ''}
            </div>
            <button class="btn btn-outline btn-sm" id="btnUserLogout">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
            </button>
        `;

        const logoutBtn = document.getElementById('btnUserLogout');
        if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

        // Auto-fill student registration form if logged in as student
        if (!isAdmin) {
            const regName = document.getElementById('regName');
            const regUid = document.getElementById('regUid');
            const regEmail = document.getElementById('regEmail');
            const regDept = document.getElementById('regDept');

            if (regName && currentUser.name) regName.value = currentUser.name;
            if (regUid && currentUser.uid) regUid.value = currentUser.uid;
            if (regEmail && currentUser.email) regEmail.value = currentUser.email;
            if (regDept && currentUser.department) regDept.value = currentUser.department;

            if (sessionStatusCard) {
                sessionStatusCard.innerHTML = `
                    <i class="fa-solid fa-circle-check text-success"></i>
                    <span>Signed in as <b>${currentUser.name}</b> (${currentUser.uid}). Profile details auto-filled!</span>
                `;
            }
        }

        // Admin view states
        if (isAdmin) {
            if (adminLockScreen) adminLockScreen.style.display = 'none';
            if (adminDashboardView) adminDashboardView.style.display = 'block';
            adminCols.forEach(col => col.style.display = 'table-cell');
            
            const adminNameText = document.getElementById('adminNameText');
            if (adminNameText) adminNameText.innerText = currentUser.name || 'Club Administrator';

            const btnAdminLogout = document.getElementById('btnAdminLogout');
            if (btnAdminLogout) btnAdminLogout.addEventListener('click', handleLogout);
        } else {
            if (adminLockScreen) adminLockScreen.style.display = 'block';
            if (adminDashboardView) adminDashboardView.style.display = 'none';
            adminCols.forEach(col => col.style.display = 'none');
        }
    } else {
        navActions.innerHTML = `
            <button class="btn btn-outline" id="btnLoginModal">
                <i class="fa-solid fa-right-to-bracket"></i> Login
            </button>
            <button class="btn btn-primary" id="btnRegisterModal">
                <i class="fa-solid fa-id-card"></i> Sign Up
            </button>
        `;
        document.getElementById('btnLoginModal').addEventListener('click', () => openAuthModal('studentLogin'));
        document.getElementById('btnRegisterModal').addEventListener('click', () => openAuthModal('studentRegister'));

        if (adminLockScreen) adminLockScreen.style.display = 'block';
        if (adminDashboardView) adminDashboardView.style.display = 'none';
        adminCols.forEach(col => col.style.display = 'none');

        if (sessionStatusCard) {
            sessionStatusCard.innerHTML = `
                <i class="fa-solid fa-circle-info"></i>
                <span>Not logged in? You can still register directly, or <a href="javascript:void(0)" onclick="openAuthModal('studentLogin')">log in</a> to auto-fill your profile.</span>
            `;
        }
    }

    renderMembersTable();
}

function handleLogout() {
    currentUser = null;
    localStorage.removeItem('tec_user_session');
    showToast('You have signed out successfully.', 'info');
    updateUserNavState();
}

/* ==========================================================================
   STATS FETCHING
   ========================================================================== */
async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (data.success) {
            document.getElementById('statTotalMembers').innerText = data.stats.total_members;
            document.getElementById('statTotalEvents').innerText = data.stats.total_events;
            document.getElementById('statSportsCount').innerText = data.stats.sports_count;
            document.getElementById('statCulturalCount').innerText = (data.stats.cultural_count + data.stats.arts_count);
        }
    } catch (e) {
        // Fallback calculation from local data
        document.getElementById('statTotalMembers').innerText = currentMembers.length || 6;
        document.getElementById('statTotalEvents').innerText = currentEvents.length || 13;
        document.getElementById('statSportsCount').innerText = 3;
        document.getElementById('statCulturalCount').innerText = 3;
    }
}

/* ==========================================================================
   EVENT MANAGEMENT & DISPLAY
   ========================================================================== */
async function loadEvents() {
    const container = document.getElementById('eventsContainer');
    try {
        const res = await fetch('/api/events');
        const data = await res.json();
        if (data.success && data.events.length > 0) {
            currentEvents = data.events;
        } else {
            currentEvents = SEED_EVENTS;
        }
    } catch (e) {
        currentEvents = SEED_EVENTS;
    }

    renderEventsGrid();
    updateEventDropdown('Sports');
}

function renderEventsGrid() {
    const container = document.getElementById('eventsContainer');
    if (!container) return;

    const searchTerm = (document.getElementById('eventSearchInput')?.value || '').toLowerCase().trim();

    const filtered = currentEvents.filter(ev => {
        const matchCat = (activeCategoryFilter === 'All' || ev.category.toLowerCase() === activeCategoryFilter.toLowerCase());
        const matchSearch = (!searchTerm || ev.title.toLowerCase().includes(searchTerm) || ev.venue.toLowerCase().includes(searchTerm) || ev.description.toLowerCase().includes(searchTerm));
        return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-calendar-xmark text-muted"></i>
                <p>No events found matching your filter.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(ev => {
        const catBadgeClass = ev.category.toLowerCase() === 'sports' ? 'sports-badge' : (ev.category.toLowerCase() === 'cultural' ? 'cultural-badge' : 'arts-badge');
        const catIcon = ev.category.toLowerCase() === 'sports' ? 'fa-medal' : (ev.category.toLowerCase() === 'cultural' ? 'fa-music' : 'fa-palette');

        return `
            <div class="event-card">
                <div>
                    <div class="event-card-header">
                        <span class="category-badge ${catBadgeClass}">
                            <i class="fa-solid ${catIcon}"></i> ${ev.category}
                        </span>
                        <span class="text-dim" style="font-size:0.75rem;"><i class="fa-solid fa-users"></i> ${ev.max_seats || 50} Max</span>
                    </div>
                    <h4>${ev.title}</h4>
                    <p>${ev.description || 'Inter-department club championship.'}</p>
                </div>
                <div>
                    <div class="event-meta">
                        <span><i class="fa-regular fa-calendar"></i> ${ev.date || 'TBD'}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${ev.venue || 'Club Arena'}</span>
                    </div>
                    <button class="btn btn-outline btn-block btn-sm" onclick="selectEventForRegistration('${ev.category}', '${ev.title.replace(/'/g, "\\'")}')">
                        <i class="fa-solid fa-pen-to-square"></i> Register For This Event
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function filterEventsByCategory(category) {
    activeCategoryFilter = category;
    const pills = document.querySelectorAll('.filter-pill');
    pills.forEach(p => {
        if (p.dataset.category.toLowerCase() === category.toLowerCase()) p.classList.add('active');
        else p.classList.remove('active');
    });
    renderEventsGrid();
    const eventsElem = document.getElementById('events');
    if (eventsElem) eventsElem.scrollIntoView({ behavior: 'smooth' });
}

function selectEventForRegistration(category, eventTitle) {
    // Select radio
    const radios = document.querySelectorAll('input[name="eventCategoryRadio"]');
    radios.forEach(r => {
        if (r.value.toLowerCase() === category.toLowerCase()) {
            r.checked = true;
        }
    });

    updateEventDropdown(category);

    const dropdown = document.getElementById('regEventSelect');
    if (dropdown) {
        // Find matching option
        for (let i = 0; i < dropdown.options.length; i++) {
            if (dropdown.options[i].value.includes(eventTitle)) {
                dropdown.selectedIndex = i;
                break;
            }
        }
    }

    const regSection = document.getElementById('register');
    if (regSection) regSection.scrollIntoView({ behavior: 'smooth' });
    showToast(`Selected event: ${eventTitle}`, 'info');
}

function initEventCategoryRadios() {
    const radios = document.querySelectorAll('input[name="eventCategoryRadio"]');
    radios.forEach(r => {
        r.addEventListener('change', (e) => {
            updateEventDropdown(e.target.value);
        });
    });

    // Filter pills
    const pills = document.querySelectorAll('.filter-pill');
    pills.forEach(p => {
        p.addEventListener('click', () => {
            filterEventsByCategory(p.dataset.category);
        });
    });

    // Event search input
    const searchInput = document.getElementById('eventSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', renderEventsGrid);
    }
}

function updateEventDropdown(category) {
    const dropdown = document.getElementById('regEventSelect');
    if (!dropdown) return;

    dropdown.innerHTML = '';

    const matching = currentEvents.filter(ev => ev.category.toLowerCase() === category.toLowerCase());

    if (matching.length === 0) {
        // Fallback defaults
        let defaults = [];
        if (category === 'Sports') {
            defaults = ["Cricket", "Football", "Badminton", "Basketball", "Kabaddi", "Volleyball", "Table Tennis"];
        } else if (category === 'Cultural') {
            defaults = ["Vocal & Instrumental Music", "Choreography & Dance", "Skits & Theatrical Drama", "Standup Comedy"];
        } else {
            defaults = ["Canvas Oil & Watercolor Painting", "Pencil Sketching & Caricature", "Digital Illustration & Design"];
        }
        defaults.forEach(item => {
            const opt = document.createElement('option');
            opt.value = `${category} Event: ${item}`;
            opt.textContent = item;
            dropdown.appendChild(opt);
        });
        return;
    }

    matching.forEach(ev => {
        const opt = document.createElement('option');
        opt.value = `${ev.category} Event: ${ev.title}`;
        opt.textContent = `${ev.title} (${ev.date || 'TBD'})`;
        dropdown.appendChild(opt);
    });
}

/* ==========================================================================
   MEMBERS DIRECTORY & REGISTRATION
   ========================================================================== */
async function loadMembers() {
    try {
        const res = await fetch('/api/members');
        const data = await res.json();
        if (data.success && data.members) {
            currentMembers = data.members;
        } else {
            currentMembers = SEED_MEMBERS;
        }
    } catch (e) {
        currentMembers = SEED_MEMBERS;
    }

    renderMembersTable();
}

function renderMembersTable() {
    const tbody = document.getElementById('membersTableBody');
    const countLabel = document.getElementById('memberCountLabel');
    if (!tbody) return;

    const searchTerm = (document.getElementById('memberSearchInput')?.value || '').toLowerCase().trim();
    const eventFilter = document.getElementById('filterEventSelect')?.value || 'All';
    const deptFilter = document.getElementById('filterDeptSelect')?.value || 'All';

    const isAdmin = currentUser && currentUser.role === 'admin';

    const filtered = currentMembers.filter(m => {
        const matchSearch = (!searchTerm || 
            (m.name && m.name.toLowerCase().includes(searchTerm)) || 
            (m.uid && m.uid.toLowerCase().includes(searchTerm)) || 
            (m.email && m.email.toLowerCase().includes(searchTerm))
        );
        const matchEvent = (eventFilter === 'All' || (m.event && m.event.toLowerCase().includes(eventFilter.toLowerCase())));
        const matchDept = (deptFilter === 'All' || m.department === deptFilter);
        return matchSearch && matchEvent && matchDept;
    });

    if (countLabel) {
        countLabel.innerText = `Showing ${filtered.length} of ${currentMembers.length} enrolled members`;
    }

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="${isAdmin ? 7 : 6}" class="text-center py-4 text-muted">
                    <i class="fa-solid fa-folder-open" style="font-size:1.5rem; margin-bottom:0.5rem; display:block;"></i>
                    No member records found matching the filter criteria.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filtered.map(m => `
        <tr>
            <td><b>#${m.id || m.rowid || '-'}</b></td>
            <td><i class="fa-regular fa-user text-primary" style="margin-right:0.4rem;"></i> <b>${m.name}</b></td>
            <td><span class="dept-badge">${m.department}</span></td>
            <td><code>${m.uid}</code></td>
            <td class="text-dim">${m.email}</td>
            <td><span class="event-cell-tag">${m.event}</span></td>
            ${isAdmin ? `
                <td class="admin-only-col">
                    <button class="btn-delete-row" onclick="deleteMemberRegistration(${m.id || m.rowid})">
                        <i class="fa-solid fa-trash"></i> Delete
                    </button>
                </td>
            ` : ''}
        </tr>
    `).join('');
}

async function deleteMemberRegistration(id) {
    if (!confirm(`Are you sure you want to permanently remove registration #${id}?`)) return;

    try {
        const res = await fetch(`/api/member/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            currentMembers = currentMembers.filter(m => (m.id !== id && m.rowid !== id));
            renderMembersTable();
            fetchStats();
        } else {
            showToast(data.message || 'Error deleting member', 'error');
        }
    } catch (e) {
        currentMembers = currentMembers.filter(m => (m.id !== id && m.rowid !== id));
        renderMembersTable();
        showToast(`Registration #${id} deleted from local state.`, 'success');
    }
}

/* ==========================================================================
   FORM HANDLERS
   ========================================================================== */
function initForms() {
    // Member Event Registration Form
    const regForm = document.getElementById('eventRegistrationForm');
    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const uid = document.getElementById('regUid').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const department = document.getElementById('regDept').value;
            const event = document.getElementById('regEventSelect').value;

            if (!name || !uid || !email || !department || !event) {
                showToast('Please complete all registration fields.', 'warning');
                return;
            }

            const btn = document.getElementById('btnSubmitRegistration');
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';

            try {
                const res = await fetch('/api/member/register-event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, uid, email, department, event })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Member Registered Successfully!', 'success');
                    currentMembers.unshift(data.member);
                    renderMembersTable();
                    fetchStats();
                    showConfirmationTicket(data.member);
                    regForm.reset();
                    // Restore category dropdown
                    updateEventDropdown('Sports');
                } else {
                    showToast(data.message || 'Registration failed', 'error');
                }
            } catch (err) {
                // Client-side fallback
                const newMember = {
                    id: Date.now().toString().slice(-4),
                    name, uid, email, department, event
                };
                currentMembers.unshift(newMember);
                renderMembersTable();
                showToast('Member Registered Successfully!', 'success');
                showConfirmationTicket(newMember);
                regForm.reset();
                updateEventDropdown('Sports');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Complete Registration';
            }
        });
    }

    // Student Login Form
    const studentLoginForm = document.getElementById('studentLoginForm');
    if (studentLoginForm) {
        studentLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value.trim();
            const password = document.getElementById('loginPassword').value.trim();

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (data.success) {
                    currentUser = data.user;
                    localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                    showToast(data.message, 'success');
                    closeAuthModal();
                    updateUserNavState();
                } else {
                    showToast(data.message || 'Login failed', 'error');
                }
            } catch (err) {
                // Offline fallback login for demo
                if (username && password) {
                    currentUser = {
                        name: username.toUpperCase(),
                        username: username,
                        uid: 'UID-' + Math.floor(1000 + Math.random() * 9000),
                        email: `${username.toLowerCase()}@example.com`,
                        department: 'CSE',
                        role: 'student'
                    };
                    localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                    showToast(`Logged in as ${username}`, 'success');
                    closeAuthModal();
                    updateUserNavState();
                }
            }
        });
    }

    // Student Sign Up Form
    const signUpForm = document.getElementById('userSignUpForm');
    if (signUpForm) {
        signUpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('signUpName').value.trim();
            const uid = document.getElementById('signUpUid').value.trim();
            const department = document.getElementById('signUpDept').value;
            const email = document.getElementById('signUpEmail').value.trim();
            const username = document.getElementById('signUpUsername').value.trim();
            const password = document.getElementById('signUpPassword').value.trim();

            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, uid, department, email, username, password, role: 'student' })
                });
                const data = await res.json();
                if (data.success) {
                    currentUser = data.user;
                    localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                    showToast('Account registered and logged in!', 'success');
                    closeAuthModal();
                    updateUserNavState();
                } else {
                    showToast(data.message || 'Registration error', 'error');
                }
            } catch (err) {
                currentUser = { name, uid, department, email, username, role: 'student' };
                localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                showToast('Registration successful!', 'success');
                closeAuthModal();
                updateUserNavState();
            }
        });
    }

    // Admin Login Form
    const adminLoginForm = document.getElementById('adminLoginForm');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('adminUser').value.trim();
            const password = document.getElementById('adminPass').value.trim();

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (data.success && data.user.role === 'admin') {
                    currentUser = data.user;
                    localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                    showToast('Admin Authorization Successful!', 'success');
                    closeAuthModal();
                    updateUserNavState();
                    const adminSec = document.getElementById('admin');
                    if (adminSec) adminSec.scrollIntoView({ behavior: 'smooth' });
                } else if (data.success) {
                    showToast('Unauthorized: This account does not have admin privileges.', 'warning');
                } else {
                    showToast(data.message || 'Admin login failed', 'error');
                }
            } catch (err) {
                if (username === 'admin' && (password === 'admin123' || password === 'admin')) {
                    currentUser = {
                        name: 'Master Administrator',
                        username: 'admin',
                        role: 'admin'
                    };
                    localStorage.setItem('tec_user_session', JSON.stringify(currentUser));
                    showToast('Admin authorized in offline mode!', 'success');
                    closeAuthModal();
                    updateUserNavState();
                } else {
                    showToast('Invalid admin credentials', 'error');
                }
            }
        });
    }

    // Admin Add Event Form
    const addEventForm = document.getElementById('adminAddEventForm');
    if (addEventForm) {
        addEventForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('newEventTitle').value.trim();
            const category = document.getElementById('newEventCategory').value;
            const max_seats = parseInt(document.getElementById('newEventSeats').value) || 50;
            const date = document.getElementById('newEventDate').value;
            const venue = document.getElementById('newEventVenue').value.trim();
            const description = document.getElementById('newEventDesc').value.trim();

            try {
                const res = await fetch('/api/events', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, category, max_seats, date, venue, description })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('New Event Created Successfully!', 'success');
                    currentEvents.unshift({ id: data.id, title, category, max_seats, date, venue, description });
                    renderEventsGrid();
                    fetchStats();
                    addEventForm.reset();
                } else {
                    showToast(data.message, 'error');
                }
            } catch (err) {
                currentEvents.unshift({ id: Date.now(), title, category, max_seats, date, venue, description });
                renderEventsGrid();
                showToast('Event added locally!', 'success');
                addEventForm.reset();
            }
        });
    }

    // Search and filter listeners for directory
    const memberSearch = document.getElementById('memberSearchInput');
    const filterEvent = document.getElementById('filterEventSelect');
    const filterDept = document.getElementById('filterDeptSelect');
    const btnRefresh = document.getElementById('btnRefreshMembers');

    if (memberSearch) memberSearch.addEventListener('input', renderMembersTable);
    if (filterEvent) filterEvent.addEventListener('change', renderMembersTable);
    if (filterDept) filterDept.addEventListener('change', renderMembersTable);
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            loadMembers();
            fetchStats();
            showToast('Refreshed directory records.', 'info');
        });
    }

    // CSV Export button
    const btnExportCsv = document.getElementById('btnExportCsv');
    if (btnExportCsv) {
        btnExportCsv.addEventListener('click', () => {
            window.location.href = '/api/export-csv';
        });
    }
}

/* ==========================================================================
   CONFIRMATION TICKET MODAL
   ========================================================================== */
function showConfirmationTicket(member) {
    const modal = document.getElementById('ticketModal');
    if (!modal) return;

    document.getElementById('ticketName').innerText = member.name;
    document.getElementById('ticketUid').innerText = member.uid;
    document.getElementById('ticketDept').innerText = member.department;
    document.getElementById('ticketRegId').innerText = `#TEC-${new Date().getFullYear()}-${member.id || Math.floor(100 + Math.random() * 900)}`;
    document.getElementById('ticketEvent').innerText = member.event;

    modal.classList.add('active');
}

/* ==========================================================================
   TOAST NOTIFICATION UTILITY
   ========================================================================== */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-triangle-exclamation';
    if (type === 'warning') icon = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(40px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
