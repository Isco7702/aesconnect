/* ══════════════════════════════════════════════════════════════
   AES CONNECT - APPLICATION JAVASCRIPT
   Le reseau social de l'Alliance des Etats du Sahel
   ══════════════════════════════════════════════════════════════ */

const API = '';
let currentUser = null;
let token = localStorage.getItem('aes_token');
let currentPage = 'feed';
let feedPage = 1;
let feedLoading = false;
let feedHasMore = true;
let currentChatUserId = null;
let chatPollInterval = null;
let postImages = [];
let postFeeling = '';
let postLocation = '';
let viewingProfileUsername = null;

// ══════ API HELPERS ══════

async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
        const res = await fetch(`${API}${path}`, { ...options, headers: { ...headers, ...(options.headers || {}) } });
        const data = await res.json();
        if (res.status === 401 && path !== '/api/auth/login') {
            handleLogout();
            return { success: false, error: 'Session expiree' };
        }
        return data;
    } catch (e) {
        console.error('API Error:', e);
        return { success: false, error: 'Erreur de connexion au serveur' };
    }
}

function apiGet(path) { return api(path); }
function apiPost(path, body) { return api(path, { method: 'POST', body: JSON.stringify(body) }); }
function apiPut(path, body) { return api(path, { method: 'PUT', body: JSON.stringify(body) }); }
function apiDelete(path) { return api(path, { method: 'DELETE' }); }

// ══════ TOAST NOTIFICATIONS ══════

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${icons[type]}"></i><span>${message}</span><span class="toast-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></span>`;
    container.appendChild(toast);
    setTimeout(() => { if (toast.parentElement) toast.remove(); }, 4000);
}

// ══════ AUTH ══════

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.auth-tab[data-tab="${tab}"]`).classList.add('active');
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${tab}-form`).classList.add('active');
    hideAuthError();

    const indicator = document.querySelector('.tab-indicator');
    if (tab === 'register') {
        indicator.style.transform = 'translateX(100%)';
    } else {
        indicator.style.transform = 'translateX(0)';
    }
}

function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg;
    el.classList.remove('hidden');
}
function hideAuthError() { document.getElementById('auth-error').classList.add('hidden'); }

async function handleLogin(e) {
    e.preventDefault();
    hideAuthError();
    const btn = document.getElementById('login-btn');
    btn.querySelector('span').textContent = 'Connexion...';
    btn.querySelector('.btn-loader').classList.remove('hidden');
    btn.disabled = true;

    const data = await apiPost('/api/auth/login', {
        login: document.getElementById('login-id').value.trim(),
        password: document.getElementById('login-password').value
    });

    btn.querySelector('span').textContent = 'Se connecter';
    btn.querySelector('.btn-loader').classList.add('hidden');
    btn.disabled = false;

    if (data.success) {
        token = data.token;
        localStorage.setItem('aes_token', token);
        currentUser = data.user;
        showApp();
        showToast('Bienvenue, ' + currentUser.full_name + ' !', 'success');
    } else {
        showAuthError(data.error || 'Erreur de connexion');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    hideAuthError();
    const btn = document.getElementById('register-btn');
    btn.querySelector('span').textContent = 'Creation...';
    btn.querySelector('.btn-loader').classList.remove('hidden');
    btn.disabled = true;

    const data = await apiPost('/api/auth/register', {
        full_name: document.getElementById('reg-fullname').value.trim(),
        username: document.getElementById('reg-username').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        password: document.getElementById('reg-password').value,
        country: document.getElementById('reg-country').value
    });

    btn.querySelector('span').textContent = 'Creer mon compte';
    btn.querySelector('.btn-loader').classList.add('hidden');
    btn.disabled = false;

    if (data.success) {
        token = data.token;
        localStorage.setItem('aes_token', token);
        currentUser = data.user;
        showApp();
        showToast('Bienvenue sur AES Connect, ' + currentUser.full_name + ' !', 'success');
    } else {
        showAuthError(data.error || "Erreur lors de l'inscription");
    }
}

function handleLogout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('aes_token');
    if (chatPollInterval) clearInterval(chatPollInterval);
    showLanding();
    showToast('Deconnexion reussie', 'info');
}

// ══════ PASSWORD STRENGTH ══════

document.addEventListener('DOMContentLoaded', () => {
    const pwdInput = document.getElementById('reg-password');
    if (pwdInput) {
        pwdInput.addEventListener('input', (e) => {
            const pwd = e.target.value;
            const fill = document.querySelector('.strength-fill');
            const text = document.querySelector('.strength-text');
            let score = 0;
            if (pwd.length >= 8) score++;
            if (/[A-Z]/.test(pwd)) score++;
            if (/[0-9]/.test(pwd)) score++;
            if (/[^A-Za-z0-9]/.test(pwd)) score++;

            const colors = ['#DC143C', '#e67e22', '#FFD700', '#2E8B57'];
            const labels = ['Faible', 'Moyen', 'Bon', 'Fort'];
            const widths = ['25%', '50%', '75%', '100%'];

            if (pwd.length === 0) {
                fill.style.width = '0';
                text.textContent = '';
            } else {
                fill.style.width = widths[score - 1] || '10%';
                fill.style.background = colors[score - 1] || '#DC143C';
                text.textContent = labels[score - 1] || 'Tres faible';
                text.style.color = colors[score - 1] || '#DC143C';
            }
        });
    }
});

function togglePassword(btn) {
    const input = btn.parentElement.querySelector('input');
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// ══════ PAGE MANAGEMENT ══════

function showLanding() {
    document.getElementById('landing-page').classList.remove('hidden');
    document.getElementById('app').classList.add('hidden');
}

function showApp() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    setupApp();
}

async function setupApp() {
    updateUserUI();
    loadProverb();
    loadEvents();
    loadStats();
    navigateTo('feed');
    startBadgePolling();
}

function updateUserUI() {
    if (!currentUser) return;
    const avatar = getAvatarUrl(currentUser);
    const safeSetSrc = (id) => {
        const el = document.getElementById(id);
        if (el) el.src = avatar;
    };
    safeSetSrc('nav-avatar-img');
    safeSetSrc('create-post-avatar');
    safeSetSrc('modal-avatar');

    const nameEl = document.getElementById('modal-author-name');
    if (nameEl) nameEl.textContent = currentUser.full_name;

    const menuHeader = document.getElementById('user-menu-header');
    if (menuHeader) {
        menuHeader.innerHTML = `
            <img src="${avatar}" alt="" style="width:40px;height:40px;border-radius:50%;object-fit:cover">
            <div><strong>${esc(currentUser.full_name)}</strong><div style="font-size:12px;color:var(--text-muted)">@${esc(currentUser.username)}</div></div>
        `;
    }
}

function getAvatarUrl(user) {
    if (user && user.profile_picture) return user.profile_picture;
    return `https://ui-avatars.com/api/?name=${encodeURIComponent((user && user.full_name) || 'U')}&background=2E8B57&color=fff&size=200&bold=true`;
}

function getCoverUrl(user) {
    if (user && user.cover_photo) return user.cover_photo;
    return '';
}

function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatContent(text) {
    if (!text) return '';
    let html = esc(text);
    html = html.replace(/#(\w+)/g, '<span class="hashtag" onclick="searchHashtag(\'$1\')">#$1</span>');
    html = html.replace(/@(\w+)/g, '<span class="mention" onclick="viewProfile(\'$1\')">@$1</span>');
    return html;
}

function timeAgo(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = (now - date) / 1000;
    if (diff < 60) return "A l'instant";
    if (diff < 3600) return `${Math.floor(diff / 60)}min`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}j`;
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' });
}

// ══════ NAVIGATION ══════

function navigateTo(page, params = {}) {
    currentPage = page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) pageEl.classList.add('active');

    // Update sidebar
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    const sidebarLink = document.querySelector(`.sidebar-link[data-page="${page}"]`);
    if (sidebarLink) sidebarLink.classList.add('active');

    // Update bottom nav
    document.querySelectorAll('.bottom-nav-item').forEach(l => l.classList.remove('active'));
    const bottomLink = document.querySelector(`.bottom-nav-item[data-page="${page}"]`);
    if (bottomLink) bottomLink.classList.add('active');

    // Close user menu
    document.getElementById('user-menu').classList.add('hidden');

    // Load page content
    switch (page) {
        case 'feed': loadFeed(true); break;
        case 'discover': loadDiscover(); break;
        case 'profile':
            viewingProfileUsername = params.username || currentUser.username;
            loadProfile(viewingProfileUsername);
            break;
        case 'groups': loadGroups(); break;
        case 'group-detail': loadGroupDetail(params.groupId); break;
        case 'messages': loadConversations(); break;
        case 'notifications': loadNotifications(); break;
        case 'saved': loadSaved(); break;
        case 'settings': loadSettings(); break;
    }
    window.scrollTo(0, 0);
}

function toggleUserMenu() {
    document.getElementById('user-menu').classList.toggle('hidden');
}

// Close menu on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('user-menu');
    const avatar = document.getElementById('nav-avatar');
    if (menu && avatar && !menu.contains(e.target) && !avatar.contains(e.target)) {
        menu.classList.add('hidden');
    }
    const searchDropdown = document.getElementById('search-dropdown');
    const searchBar = document.getElementById('global-search');
    if (searchDropdown && searchBar && !searchBar.contains(e.target)) {
        searchDropdown.classList.add('hidden');
    }
});

// ══════ FEED ══════

async function loadFeed(reset = false) {
    if (reset) {
        feedPage = 1;
        feedHasMore = true;
        document.getElementById('feed-posts').innerHTML = '';
    }
    if (feedLoading || !feedHasMore) return;
    feedLoading = true;
    document.getElementById('feed-loader').classList.remove('hidden');

    const data = await apiGet(`/api/posts?page=${feedPage}`);
    document.getElementById('feed-loader').classList.add('hidden');
    feedLoading = false;

    if (data.success) {
        const container = document.getElementById('feed-posts');
        if (data.posts.length === 0 && feedPage === 1) {
            // Try explore feed
            const explore = await apiGet(`/api/posts/explore?page=1`);
            if (explore.success && explore.posts.length > 0) {
                explore.posts.forEach(p => container.appendChild(createPostCard(p)));
            } else {
                document.getElementById('feed-empty').classList.remove('hidden');
            }
        } else {
            document.getElementById('feed-empty').classList.add('hidden');
            data.posts.forEach(p => container.appendChild(createPostCard(p)));
            feedHasMore = data.has_next;
            feedPage++;
        }
    }
}

// Infinite scroll
window.addEventListener('scroll', () => {
    if (currentPage !== 'feed') return;
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 300) {
        loadFeed();
    }
});

// ══════ POST CARD ══════

function createPostCard(post) {
    const div = document.createElement('div');
    div.className = 'post-card';
    div.id = `post-${post.id}`;

    const author = post.author || {};
    const avatar = getAvatarUrl(author);
    const images = post.images || [];

    let imagesHtml = '';
    if (images.length === 1) {
        imagesHtml = `<div class="post-images" onclick="openImage('${images[0]}')"><img src="${images[0]}" alt="Post image" loading="lazy"></div>`;
    } else if (images.length > 1) {
        const gridClass = images.length === 2 ? 'grid-2' : images.length === 3 ? 'grid-3' : 'grid-4';
        const displayImages = images.slice(0, 4);
        imagesHtml = `<div class="post-images post-images-grid ${gridClass}">${displayImages.map(img => `<img src="${img}" alt="" loading="lazy" onclick="openImage('${img}')">`).join('')}</div>`;
    }

    const feelingHtml = post.feeling ? `<span class="post-feeling"> - se sent ${esc(post.feeling)}</span>` : '';
    const locationHtml = post.location ? `<span class="post-location"><i class="fas fa-map-marker-alt"></i> ${esc(post.location)}</span>` : '';
    const verifiedHtml = author.is_verified ? '<i class="fas fa-check-circle verified"></i>' : '';

    const likeClass = post.user_reaction ? 'liked' : '';
    const saveClass = post.is_saved ? 'saved' : '';
    const reactionEmojis = { 'like': '❤️', 'love': '💕', 'support': '🙏', 'celebrate': '🎉', 'think': '🤔' };
    const likeIcon = post.user_reaction ? (reactionEmojis[post.user_reaction] || '❤️') : '<i class="far fa-heart"></i>';
    const saveIcon = post.is_saved ? '<i class="fas fa-bookmark"></i>' : '<i class="far fa-bookmark"></i>';

    div.innerHTML = `
        <div class="post-header">
            <img src="${avatar}" alt="" class="post-avatar" onclick="viewProfile('${esc(author.username)}')">
            <div class="post-meta">
                <div class="post-author" onclick="viewProfile('${esc(author.username)}')">
                    ${esc(author.full_name)} ${verifiedHtml} ${feelingHtml}
                </div>
                <div class="post-time">${timeAgo(post.created_at)} ${locationHtml}</div>
            </div>
            <button class="post-menu-btn" onclick="togglePostMenu(${post.id})"><i class="fas fa-ellipsis-h"></i></button>
        </div>
        ${post.content ? `<div class="post-content">${formatContent(post.content)}</div>` : ''}
        ${imagesHtml}
        <div class="post-stats">
            <span class="likes-stat">${post.likes_count > 0 ? `❤️ ${post.likes_count}` : ''}</span>
            <span>${post.comments_count > 0 ? `${post.comments_count} commentaire${post.comments_count > 1 ? 's' : ''}` : ''} ${post.shares_count > 0 ? ` &middot; ${post.shares_count} partage${post.shares_count > 1 ? 's' : ''}` : ''}</span>
        </div>
        <div class="post-actions">
            <button class="post-action-btn ${likeClass}" onclick="toggleLike(${post.id})" onmouseenter="showReactions(this, ${post.id})" onmouseleave="hideReactions(this)">
                <span class="like-icon">${likeIcon}</span>
                <span>${post.user_reaction ? 'Aime' : "J'aime"}</span>
            </button>
            <button class="post-action-btn" onclick="toggleComments(${post.id})">
                <i class="far fa-comment"></i> Commenter
            </button>
            <button class="post-action-btn ${saveClass}" onclick="toggleSave(${post.id})">
                ${saveIcon} <span class="save-text">${post.is_saved ? 'Enregistre' : 'Enregistrer'}</span>
            </button>
        </div>
        <div class="comments-section hidden" id="comments-${post.id}">
            <div class="comments-list" id="comments-list-${post.id}"></div>
            <div class="comment-input-row">
                <img src="${getAvatarUrl(currentUser)}" alt="" class="avatar-xs">
                <input type="text" placeholder="Ecrire un commentaire..." onkeydown="if(event.key==='Enter')submitComment(${post.id}, this)">
                <button onclick="submitComment(${post.id}, this.previousElementSibling)"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    `;
    return div;
}

// ══════ LIKES & REACTIONS ══════

let reactionsTimeout;

function showReactions(btn, postId) {
    clearTimeout(reactionsTimeout);
    hideAllReactions();
    const popup = document.createElement('div');
    popup.className = 'reactions-popup';
    popup.id = 'reactions-popup';
    const reactions = [
        { type: 'like', emoji: '❤️' },
        { type: 'love', emoji: '💕' },
        { type: 'support', emoji: '🙏' },
        { type: 'celebrate', emoji: '🎉' },
        { type: 'think', emoji: '🤔' }
    ];
    reactions.forEach(r => {
        popup.innerHTML += `<span class="reaction-btn" onclick="event.stopPropagation(); reactToPost(${postId}, '${r.type}')" title="${r.type}">${r.emoji}</span>`;
    });
    btn.style.position = 'relative';
    btn.appendChild(popup);
}

function hideReactions(btn) {
    reactionsTimeout = setTimeout(() => { hideAllReactions(); }, 500);
}

function hideAllReactions() {
    document.querySelectorAll('.reactions-popup').forEach(p => p.remove());
}

async function reactToPost(postId, reaction) {
    hideAllReactions();
    const data = await apiPost(`/api/posts/${postId}/like`, { reaction });
    if (data.success) refreshPost(postId);
}

async function toggleLike(postId) {
    const data = await apiPost(`/api/posts/${postId}/like`, { reaction: 'like' });
    if (data.success) refreshPost(postId);
}

async function toggleSave(postId) {
    const data = await apiPost(`/api/posts/${postId}/save`);
    if (data.success) {
        showToast(data.saved ? 'Publication enregistree' : 'Publication retiree', 'success');
        refreshPost(postId);
    }
}

async function refreshPost(postId) {
    const data = await apiGet(`/api/posts/${postId}`);
    if (data.success) {
        const old = document.getElementById(`post-${postId}`);
        if (old) {
            const newCard = createPostCard(data.post);
            // preserve comments visibility
            const oldComments = old.querySelector('.comments-section');
            if (oldComments && !oldComments.classList.contains('hidden')) {
                newCard.querySelector('.comments-section').classList.remove('hidden');
                newCard.querySelector('.comments-list').innerHTML = oldComments.querySelector('.comments-list').innerHTML;
            }
            old.replaceWith(newCard);
        }
    }
}

// ══════ COMMENTS ══════

async function toggleComments(postId) {
    const section = document.getElementById(`comments-${postId}`);
    if (section.classList.contains('hidden')) {
        section.classList.remove('hidden');
        loadComments(postId);
    } else {
        section.classList.add('hidden');
    }
}

async function loadComments(postId) {
    const data = await apiGet(`/api/posts/${postId}/comments`);
    const container = document.getElementById(`comments-list-${postId}`);
    if (data.success) {
        container.innerHTML = data.comments.map(c => createCommentHtml(c, postId)).join('');
    }
}

function createCommentHtml(comment, postId) {
    const author = comment.author || {};
    const avatar = getAvatarUrl(author);
    return `
        <div class="comment">
            <img src="${avatar}" alt="" class="comment-avatar" onclick="viewProfile('${esc(author.username)}')">
            <div class="comment-body">
                <div class="comment-bubble">
                    <div class="comment-author" onclick="viewProfile('${esc(author.username)}')">${esc(author.full_name)}</div>
                    <div class="comment-text">${formatContent(comment.content)}</div>
                </div>
                <div class="comment-meta">
                    <span>${timeAgo(comment.created_at)}</span>
                    ${comment.reply_count > 0 ? `<button onclick="loadReplies(${comment.id}, ${postId})">${comment.reply_count} reponse(s)</button>` : ''}
                    <button onclick="replyToComment(${postId}, ${comment.id}, '${esc(author.full_name)}')">Repondre</button>
                </div>
                <div id="replies-${comment.id}"></div>
            </div>
        </div>
    `;
}

async function submitComment(postId, input) {
    const content = input.value.trim();
    if (!content) return;
    const parentId = input.dataset.parentId || null;
    const data = await apiPost(`/api/posts/${postId}/comments`, { content, parent_id: parentId ? parseInt(parentId) : null });
    if (data.success) {
        input.value = '';
        delete input.dataset.parentId;
        input.placeholder = 'Ecrire un commentaire...';
        loadComments(postId);
        // Update comment count visually
        refreshPost(postId);
    }
}

function replyToComment(postId, commentId, authorName) {
    const section = document.getElementById(`comments-${postId}`);
    const input = section.querySelector('.comment-input-row input');
    input.dataset.parentId = commentId;
    input.placeholder = `Repondre a ${authorName}...`;
    input.focus();
}

async function loadReplies(commentId, postId) {
    const data = await apiGet(`/api/comments/${commentId}/replies`);
    if (data.success) {
        const container = document.getElementById(`replies-${commentId}`);
        container.innerHTML = data.replies.map(r => createCommentHtml(r, postId)).join('');
    }
}

// ══════ CREATE POST ══════

function openPostModal(focus) {
    document.getElementById('post-modal').classList.remove('hidden');
    document.getElementById('post-content').focus();
    postImages = [];
    postFeeling = '';
    postLocation = '';
    document.getElementById('post-images-preview').innerHTML = '';
    document.getElementById('post-feeling-display').classList.add('hidden');
    document.getElementById('post-location-display').classList.add('hidden');
    document.getElementById('feeling-picker').classList.add('hidden');
}

function closePostModal() {
    document.getElementById('post-modal').classList.add('hidden');
    document.getElementById('post-content').value = '';
    postImages = [];
}

function handlePostImages(input) {
    const files = Array.from(input.files);
    const preview = document.getElementById('post-images-preview');

    files.forEach(file => {
        if (postImages.length >= 10) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const url = e.target.result;
            postImages.push(url);
            const idx = postImages.length - 1;
            preview.innerHTML += `
                <div class="preview-img" id="preview-${idx}">
                    <img src="${url}" alt="">
                    <span class="remove-img" onclick="removePostImage(${idx})"><i class="fas fa-times"></i></span>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    });
    input.value = '';
}

function removePostImage(idx) {
    postImages[idx] = null;
    const el = document.getElementById(`preview-${idx}`);
    if (el) el.remove();
}

function toggleFeelingPicker() {
    document.getElementById('feeling-picker').classList.toggle('hidden');
}

function setFeeling(feeling, emoji) {
    postFeeling = feeling;
    const display = document.getElementById('post-feeling-display');
    display.textContent = `${emoji} ${feeling}`;
    display.classList.remove('hidden');
    document.getElementById('feeling-picker').classList.add('hidden');
}

function promptLocation() {
    const loc = prompt('Ou etes-vous ?');
    if (loc) {
        postLocation = loc;
        const display = document.getElementById('post-location-display');
        display.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${esc(loc)}`;
        display.classList.remove('hidden');
    }
}

async function submitPost() {
    const content = document.getElementById('post-content').value.trim();
    const images = postImages.filter(i => i !== null);
    const visibility = document.getElementById('post-visibility').value;

    if (!content && images.length === 0) {
        showToast('Ecrivez quelque chose ou ajoutez une image', 'error');
        return;
    }

    const btn = document.getElementById('submit-post-btn');
    btn.disabled = true;
    btn.textContent = 'Publication...';

    const data = await apiPost('/api/posts', {
        content,
        images,
        feeling: postFeeling,
        location: postLocation,
        visibility
    });

    btn.disabled = false;
    btn.textContent = 'Publier';

    if (data.success) {
        closePostModal();
        showToast('Publication creee !', 'success');
        loadFeed(true);
    } else {
        showToast(data.error || 'Erreur', 'error');
    }
}

// ══════ POST MENU ══════

function togglePostMenu(postId) {
    // Simple delete for own posts
    const post = document.getElementById(`post-${postId}`);
    if (!post) return;
    const actions = ['Supprimer', 'Signaler', 'Annuler'];
    const choice = prompt('Actions:\n1 - Supprimer (votre post)\n2 - Signaler\n3 - Annuler\n\nEntrez le numero:');
    if (choice === '1') deletePost(postId);
    else if (choice === '2') reportContent('post', postId);
}

async function deletePost(postId) {
    if (!confirm('Supprimer cette publication ?')) return;
    const data = await apiDelete(`/api/posts/${postId}`);
    if (data.success) {
        document.getElementById(`post-${postId}`)?.remove();
        showToast('Publication supprimee', 'success');
    } else {
        showToast(data.error || 'Erreur', 'error');
    }
}

async function reportContent(type, id) {
    const reason = prompt('Raison du signalement:\n1 - Spam\n2 - Harcelement\n3 - Contenu inapproprie\n4 - Autre');
    const reasons = { '1': 'Spam', '2': 'Harcelement', '3': 'Contenu inapproprie', '4': 'Autre' };
    if (reason && reasons[reason]) {
        await apiPost('/api/report', { target_type: type, target_id: id, reason: reasons[reason] });
        showToast('Signalement envoye. Merci.', 'success');
    }
}

// ══════ PROFILE ══════

async function viewProfile(username) {
    navigateTo('profile', { username });
}

async function loadProfile(username) {
    const data = await apiGet(`/api/users/${username}`);
    if (!data.success) {
        showToast('Profil non trouve', 'error');
        return;
    }

    const user = data.user;
    const avatar = getAvatarUrl(user);
    const cover = getCoverUrl(user);

    const coverEl = document.getElementById('profile-cover');
    if (cover) {
        coverEl.style.backgroundImage = `url(${cover})`;
    } else {
        coverEl.style.backgroundImage = '';
    }

    document.getElementById('profile-avatar').src = avatar;
    document.getElementById('profile-name').textContent = user.full_name;
    document.getElementById('profile-username').textContent = `@${user.username}`;
    document.getElementById('profile-bio').textContent = user.bio || '';

    const locEl = document.getElementById('profile-location');
    if (user.country || user.city) {
        locEl.classList.remove('hidden');
        locEl.querySelector('span').textContent = [user.city, user.country].filter(Boolean).join(', ');
    } else {
        locEl.classList.add('hidden');
    }

    document.getElementById('profile-joined').querySelector('span').textContent = `Membre depuis ${formatDate(user.created_at)}`;

    document.getElementById('profile-followers').textContent = user.follower_count || 0;
    document.getElementById('profile-following').textContent = user.following_count || 0;
    document.getElementById('profile-posts-count').textContent = user.post_count || 0;

    const verified = document.getElementById('profile-verified');
    if (user.is_verified) verified.classList.remove('hidden');
    else verified.classList.add('hidden');

    // Actions
    const actionsEl = document.getElementById('profile-actions');
    if (user.is_own_profile) {
        actionsEl.innerHTML = `<button class="btn-outline btn-sm" onclick="navigateTo('settings')"><i class="fas fa-edit"></i> Modifier le profil</button>`;
    } else {
        const followBtn = user.is_following
            ? `<button class="btn-outline btn-sm" onclick="toggleFollowProfile(${user.id})"><i class="fas fa-user-check"></i> Abonne</button>`
            : `<button class="btn-primary btn-sm" onclick="toggleFollowProfile(${user.id})"><i class="fas fa-user-plus"></i> Suivre</button>`;
        const msgBtn = `<button class="btn-outline btn-sm" onclick="openChat(${user.id})"><i class="fas fa-envelope"></i> Message</button>`;
        actionsEl.innerHTML = `${followBtn} ${msgBtn}`;
    }

    // Load posts
    const postsData = await apiGet(`/api/users/${user.id}/posts`);
    const container = document.getElementById('profile-posts');
    container.innerHTML = '';
    if (postsData.success && postsData.posts.length > 0) {
        postsData.posts.forEach(p => container.appendChild(createPostCard(p)));
    } else {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-pen"></i><h3>Aucune publication</h3></div>`;
    }
}

async function toggleFollowProfile(userId) {
    const data = await apiPost(`/api/users/${userId}/follow`);
    if (data.success) {
        showToast(data.following ? 'Vous suivez maintenant cet utilisateur' : 'Vous ne suivez plus cet utilisateur', 'success');
        if (viewingProfileUsername) loadProfile(viewingProfileUsername);
    }
}

function showFollowers() {
    // Show followers modal would be loaded from API
    showUsersModal('Abonnes', `/api/users/${document.getElementById('profile-followers').textContent === '0' ? currentUser.id : viewingProfileUsername}/followers`);
}

function showFollowing() {
    showUsersModal('Abonnements', `/api/users/${viewingProfileUsername || currentUser.username}/following`);
}

async function showUsersModal(title, endpoint) {
    // We need user ID, get from profile
    const profileUser = await apiGet(`/api/users/${viewingProfileUsername || currentUser.username}`);
    if (!profileUser.success) return;

    const type = endpoint.includes('followers') ? 'followers' : 'following';
    const data = await apiGet(`/api/users/${profileUser.user.id}/${type}`);

    document.getElementById('users-modal-title').textContent = title;
    const list = document.getElementById('users-modal-list');

    if (data.success && data.users.length > 0) {
        list.innerHTML = data.users.map(u => `
            <div class="user-list-item">
                <img src="${getAvatarUrl(u)}" alt="" onclick="closeUsersModal(); viewProfile('${esc(u.username)}')">
                <div class="user-info">
                    <div class="user-name" onclick="closeUsersModal(); viewProfile('${esc(u.username)}')">${esc(u.full_name)}</div>
                    <div class="user-detail">@${esc(u.username)} ${u.country ? '- ' + esc(u.country) : ''}</div>
                </div>
                <button class="btn-outline btn-sm" onclick="quickFollow(${u.id}, this)">Suivre</button>
            </div>
        `).join('');
    } else {
        list.innerHTML = '<p style="text-align:center;padding:20px;color:var(--text-muted)">Aucun utilisateur</p>';
    }

    document.getElementById('users-modal').classList.remove('hidden');
}

function closeUsersModal() { document.getElementById('users-modal').classList.add('hidden'); }

async function quickFollow(userId, btn) {
    const data = await apiPost(`/api/users/${userId}/follow`);
    if (data.success) {
        btn.textContent = data.following ? 'Abonne' : 'Suivre';
        btn.className = data.following ? 'btn-ghost btn-sm' : 'btn-outline btn-sm';
    }
}

// ══════ DISCOVER ══════

async function loadDiscover() {
    const data = await apiGet('/api/discover');
    if (!data.success) return;

    // Suggested users
    const usersContainer = document.getElementById('suggested-users');
    if (data.suggested_users.length > 0) {
        usersContainer.innerHTML = data.suggested_users.map(u => `
            <div class="user-suggestion-card">
                <img src="${getAvatarUrl(u)}" alt="" onclick="viewProfile('${esc(u.username)}')">
                <div class="suggestion-info">
                    <div class="suggestion-name" onclick="viewProfile('${esc(u.username)}')">${esc(u.full_name)}</div>
                    <div class="suggestion-meta">${u.country ? esc(u.country) : ''} &middot; ${u.follower_count} abonne(s)</div>
                </div>
                <button class="btn-primary btn-sm" onclick="quickFollow(${u.id}, this)"><i class="fas fa-user-plus"></i> Suivre</button>
            </div>
        `).join('');
    } else {
        usersContainer.innerHTML = '<p style="color:var(--text-muted);padding:16px">Aucune suggestion pour le moment</p>';
    }

    // Suggested groups
    const groupsContainer = document.getElementById('suggested-groups');
    if (data.suggested_groups.length > 0) {
        groupsContainer.innerHTML = data.suggested_groups.map(g => createGroupCardHtml(g)).join('');
    }

    // Trending posts
    const trendingContainer = document.getElementById('trending-posts');
    trendingContainer.innerHTML = '';
    if (data.trending_posts.length > 0) {
        data.trending_posts.slice(0, 10).forEach(p => trendingContainer.appendChild(createPostCard(p)));
    }

    // Trending hashtags (sidebar)
    const hashtagsContainer = document.getElementById('trending-hashtags');
    if (data.trending_hashtags.length > 0) {
        hashtagsContainer.innerHTML = data.trending_hashtags.map(h => `
            <div class="hashtag-item">
                <span class="tag" onclick="searchHashtag('${esc(h.tag)}')">#${esc(h.tag)}</span>
                <span class="count">${h.count} post(s)</span>
            </div>
        `).join('');
    } else {
        hashtagsContainer.innerHTML = '<p style="font-size:13px;color:var(--text-muted)">Publiez avec des #hashtags</p>';
    }
}

function searchHashtag(tag) {
    document.getElementById('search-input').value = `#${tag}`;
    handleSearchInput(`#${tag}`);
}

// ══════ GROUPS ══════

async function loadGroups() {
    const data = await apiGet('/api/groups');
    if (data.success) {
        const container = document.getElementById('groups-list');
        if (data.groups.length > 0) {
            container.innerHTML = data.groups.map(g => createGroupCardHtml(g)).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><h3>Aucun groupe</h3><p>Creez le premier groupe!</p></div>';
        }
    }
}

function createGroupCardHtml(group) {
    const memberLabel = group.is_member ? '<span style="color:var(--green);font-size:12px"><i class="fas fa-check"></i> Membre</span>' : '';
    return `
        <div class="group-card" onclick="navigateTo('group-detail', {groupId: ${group.id}})">
            <div class="group-cover" ${group.cover_photo ? `style="background-image:url(${group.cover_photo})"` : ''}></div>
            <div class="group-card-body">
                <div class="group-card-name">${esc(group.name)}</div>
                <div class="group-card-desc">${esc(group.description)}</div>
                <div class="group-card-meta">
                    <span class="group-card-members"><i class="fas fa-users"></i> ${group.member_count} membre(s)</span>
                    ${memberLabel}
                </div>
            </div>
        </div>
    `;
}

async function loadGroupDetail(groupId) {
    const data = await apiGet(`/api/groups/${groupId}`);
    if (!data.success) return;

    const group = data.group;
    const header = document.getElementById('group-header');
    const joinBtn = group.is_member
        ? `<button class="btn-outline btn-sm" onclick="toggleGroupMembership(${group.id})"><i class="fas fa-check"></i> Membre</button>`
        : `<button class="btn-primary btn-sm" onclick="toggleGroupMembership(${group.id})"><i class="fas fa-plus"></i> Rejoindre</button>`;

    header.innerHTML = `
        <div class="group-detail-cover" ${group.cover_photo ? `style="background-image:url(${group.cover_photo})"` : ''}></div>
        <div class="group-detail-info">
            <h2>${esc(group.name)}</h2>
            <p>${esc(group.description)}</p>
            <div class="group-detail-meta">
                <span><i class="fas fa-users"></i> ${group.member_count} membre(s)</span>
                <span><i class="fas fa-lock${group.privacy === 'public' ? '-open' : ''}"></i> ${group.privacy === 'public' ? 'Public' : 'Prive'}</span>
                ${group.category ? `<span><i class="fas fa-tag"></i> ${esc(group.category)}</span>` : ''}
            </div>
            <div class="group-detail-actions">${joinBtn}</div>
        </div>
    `;

    // Load group posts
    const postsData = await apiGet(`/api/groups/${groupId}/posts`);
    const container = document.getElementById('group-posts');
    container.innerHTML = '';

    if (group.is_member) {
        // Add create post for group
        const createDiv = document.createElement('div');
        createDiv.className = 'create-post-card';
        createDiv.innerHTML = `
            <div class="create-post-top">
                <img src="${getAvatarUrl(currentUser)}" alt="" class="avatar-sm">
                <div class="create-post-input" onclick="openGroupPost(${groupId})">Publier dans ce groupe...</div>
            </div>
        `;
        container.appendChild(createDiv);
    }

    if (postsData.success && postsData.posts.length > 0) {
        postsData.posts.forEach(p => container.appendChild(createPostCard(p)));
    }
}

async function toggleGroupMembership(groupId) {
    const data = await apiPost(`/api/groups/${groupId}/join`);
    if (data.success) {
        showToast(data.joined ? 'Vous avez rejoint le groupe!' : 'Vous avez quitte le groupe', 'success');
        loadGroupDetail(groupId);
    }
}

function openGroupPost(groupId) {
    openPostModal();
    // Override submit to include group_id
    const origSubmit = window.submitPost;
    window._groupPostId = groupId;
}

function openCreateGroupModal() {
    document.getElementById('group-modal').classList.remove('hidden');
}
function closeGroupModal() {
    document.getElementById('group-modal').classList.add('hidden');
}

async function createGroup(e) {
    e.preventDefault();
    const data = await apiPost('/api/groups', {
        name: document.getElementById('group-name').value.trim(),
        description: document.getElementById('group-description').value.trim(),
        category: document.getElementById('group-category').value,
        privacy: document.getElementById('group-privacy').value
    });

    if (data.success) {
        closeGroupModal();
        showToast('Groupe cree !', 'success');
        loadGroups();
    } else {
        showToast(data.error || 'Erreur', 'error');
    }
}

// ══════ MESSAGES ══════

async function loadConversations() {
    const data = await apiGet('/api/conversations');
    const container = document.getElementById('conversations-list');

    if (data.success) {
        if (data.conversations.length > 0) {
            container.innerHTML = data.conversations.map(c => {
                const user = c.user;
                const isActive = currentChatUserId === user.id;
                return `
                    <div class="conv-item ${isActive ? 'active' : ''}" onclick="openChat(${user.id})">
                        <img src="${getAvatarUrl(user)}" alt="">
                        <div class="conv-info">
                            <div class="conv-name">${esc(user.full_name)}</div>
                            <div class="conv-preview">${esc(c.last_message.content)}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="conv-time">${timeAgo(c.last_message.created_at)}</div>
                            ${c.unread_count > 0 ? `<div class="conv-unread">${c.unread_count}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="empty-state" style="padding:40px"><i class="fas fa-comments"></i><p>Aucune conversation</p></div>';
        }
    }
}

async function openChat(userId) {
    currentChatUserId = userId;
    const chatArea = document.getElementById('chat-area');
    const chatEmpty = document.getElementById('chat-empty');
    chatArea.classList.remove('hidden');
    chatEmpty.classList.add('hidden');

    // On mobile, hide conversation list
    const convList = document.getElementById('conversations-list');
    if (window.innerWidth <= 900) convList.classList.add('conv-hidden');

    // Get user info
    const userData = await apiGet(`/api/users/${userId}/posts`);  // Just to get name
    const user = await findUserById(userId);

    const header = document.getElementById('chat-header');
    if (user) {
        header.innerHTML = `
            ${window.innerWidth <= 900 ? '<button onclick="closeMobileChat()" style="margin-right:8px;color:var(--text-secondary)"><i class="fas fa-arrow-left"></i></button>' : ''}
            <img src="${getAvatarUrl(user)}" alt="" onclick="viewProfile('${esc(user.username)}')">
            <div class="chat-header-info">
                <div class="chat-name">${esc(user.full_name)}</div>
                <div class="chat-status">En ligne</div>
            </div>
        `;
    }

    loadMessages(userId);
    if (chatPollInterval) clearInterval(chatPollInterval);
    chatPollInterval = setInterval(() => loadMessages(userId), 5000);

    // Update conversation highlight
    loadConversations();
}

function closeMobileChat() {
    const convList = document.getElementById('conversations-list');
    convList.classList.remove('conv-hidden');
    document.getElementById('chat-area').classList.add('hidden');
    document.getElementById('chat-empty').classList.remove('hidden');
    currentChatUserId = null;
}

async function findUserById(userId) {
    // Try conversations first, then search
    const convData = await apiGet('/api/conversations');
    if (convData.success) {
        const conv = convData.conversations.find(c => c.user.id === userId);
        if (conv) return conv.user;
    }
    // Fallback: get from search
    return null;
}

async function loadMessages(userId) {
    const data = await apiGet(`/api/messages/${userId}`);
    if (data.success) {
        const container = document.getElementById('chat-messages');
        container.innerHTML = data.messages.map(m => `
            <div class="msg-bubble ${m.sender_id === currentUser.id ? 'msg-sent' : 'msg-received'}">
                ${esc(m.content)}
                <div class="msg-time">${timeAgo(m.created_at)}</div>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    }
}

async function sendMessage(e) {
    e.preventDefault();
    const input = document.getElementById('msg-input');
    const content = input.value.trim();
    if (!content || !currentChatUserId) return;

    input.value = '';
    const data = await apiPost(`/api/messages/${currentChatUserId}`, { content });
    if (data.success) {
        loadMessages(currentChatUserId);
    }
}

// ══════ NOTIFICATIONS ══════

async function loadNotifications() {
    const data = await apiGet('/api/notifications');
    if (data.success) {
        const container = document.getElementById('notifications-list');
        if (data.notifications.length > 0) {
            container.innerHTML = data.notifications.map(n => {
                const actor = n.actor || {};
                const iconMap = { like: 'like', comment: 'comment', follow: 'follow', mention: 'comment', message: 'message', group: 'follow' };
                const iconClassMap = { like: 'fa-heart', comment: 'fa-comment', follow: 'fa-user-plus', mention: 'fa-at', message: 'fa-envelope', group: 'fa-users' };
                const iconType = iconMap[n.type] || 'follow';
                const iconClass = iconClassMap[n.type] || 'fa-bell';

                return `
                    <div class="notification-item ${n.is_read ? '' : 'unread'}" onclick="markNotifRead(${n.id})">
                        ${actor.profile_picture
                            ? `<img src="${getAvatarUrl(actor)}" alt="">`
                            : `<div class="notif-icon ${iconType}"><i class="fas ${iconClass}"></i></div>`
                        }
                        <div class="notif-content">
                            <div class="notif-text">${esc(n.content)}</div>
                            <div class="notif-time">${timeAgo(n.created_at)}</div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-bell-slash"></i><h3>Aucune notification</h3><p>Vous serez notifie des activites sur votre compte.</p></div>';
        }
    }
}

async function markNotifRead(id) {
    await apiPost('/api/notifications/read', { id });
}

async function markAllNotificationsRead() {
    await apiPost('/api/notifications/read', {});
    showToast('Toutes les notifications marquees comme lues', 'success');
    loadNotifications();
    updateBadges();
}

// ══════ SAVED POSTS ══════

async function loadSaved() {
    const data = await apiGet('/api/saved');
    const container = document.getElementById('saved-posts');
    container.innerHTML = '';

    if (data.success && data.posts.length > 0) {
        data.posts.forEach(p => container.appendChild(createPostCard(p)));
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-bookmark"></i><h3>Rien d\'enregistre</h3><p>Enregistrez des publications pour les retrouver ici.</p></div>';
    }
}

// ══════ SETTINGS ══════

function loadSettings() {
    if (!currentUser) return;
    document.getElementById('set-fullname').value = currentUser.full_name || '';
    document.getElementById('set-bio').value = currentUser.bio || '';
    document.getElementById('set-country').value = currentUser.country || 'Mali';
    document.getElementById('set-city').value = currentUser.city || '';
    document.getElementById('set-phone').value = currentUser.phone || '';
    document.getElementById('set-private').checked = currentUser.is_private || false;

    const bioArea = document.getElementById('set-bio');
    document.getElementById('bio-count').textContent = (bioArea.value || '').length;
    bioArea.addEventListener('input', () => {
        document.getElementById('bio-count').textContent = bioArea.value.length;
    });
}

async function saveSettings(e) {
    e.preventDefault();
    const data = await apiPut('/api/users/profile', {
        full_name: document.getElementById('set-fullname').value.trim(),
        bio: document.getElementById('set-bio').value.trim(),
        country: document.getElementById('set-country').value,
        city: document.getElementById('set-city').value.trim(),
        phone: document.getElementById('set-phone').value.trim(),
        is_private: document.getElementById('set-private').checked
    });

    if (data.success) {
        currentUser = data.user;
        updateUserUI();
        showToast('Profil mis a jour !', 'success');
    } else {
        showToast(data.error || 'Erreur', 'error');
    }
}

// ══════ SEARCH ══════

let searchTimeout;
async function handleSearchInput(query) {
    clearTimeout(searchTimeout);
    const dropdown = document.getElementById('search-dropdown');

    if (query.length < 2) {
        dropdown.classList.add('hidden');
        return;
    }

    searchTimeout = setTimeout(async () => {
        const data = await apiGet(`/api/search?q=${encodeURIComponent(query)}`);
        if (data.success) {
            let html = '';

            if (data.users && data.users.length > 0) {
                html += '<div style="padding:8px 16px;font-size:12px;color:var(--text-muted);font-weight:600">PERSONNES</div>';
                data.users.forEach(u => {
                    html += `
                        <div class="search-result-item" onclick="viewProfile('${esc(u.username)}'); document.getElementById('search-dropdown').classList.add('hidden');">
                            <img src="${getAvatarUrl(u)}" alt="">
                            <div class="result-info">
                                <div class="result-name">${esc(u.full_name)}</div>
                                <div class="result-meta">@${esc(u.username)} ${u.country ? '- ' + esc(u.country) : ''}</div>
                            </div>
                        </div>
                    `;
                });
            }

            if (data.groups && data.groups.length > 0) {
                html += '<div style="padding:8px 16px;font-size:12px;color:var(--text-muted);font-weight:600">GROUPES</div>';
                data.groups.forEach(g => {
                    html += `
                        <div class="search-result-item" onclick="navigateTo('group-detail', {groupId: ${g.id}}); document.getElementById('search-dropdown').classList.add('hidden');">
                            <div style="width:40px;height:40px;border-radius:8px;background:var(--bg-elevated);display:flex;align-items:center;justify-content:center"><i class="fas fa-users" style="color:var(--green)"></i></div>
                            <div class="result-info">
                                <div class="result-name">${esc(g.name)}</div>
                                <div class="result-meta">${g.member_count} membre(s)</div>
                            </div>
                        </div>
                    `;
                });
            }

            if (!html) {
                html = '<div style="padding:20px;text-align:center;color:var(--text-muted)">Aucun resultat</div>';
            }

            dropdown.innerHTML = html;
            dropdown.classList.remove('hidden');
        }
    }, 300);
}

// ══════ CULTURAL CONTENT ══════

async function loadProverb() {
    const data = await apiGet('/api/proverb');
    if (data.success) {
        document.getElementById('proverb-text').textContent = `"${data.proverb.text}"`;
        document.getElementById('proverb-origin').textContent = `- ${data.proverb.origin}`;
    }
}

async function loadEvents() {
    const data = await apiGet('/api/events');
    if (data.success) {
        const container = document.getElementById('upcoming-events');
        const now = new Date();
        const currentMonth = String(now.getMonth() + 1).padStart(2, '0');
        const currentDay = String(now.getDate()).padStart(2, '0');
        const current = `${currentMonth}-${currentDay}`;

        const upcoming = data.events.filter(e => e.date >= current).slice(0, 5);
        if (upcoming.length === 0) {
            // Show next year's first events
            upcoming.push(...data.events.slice(0, 3));
        }

        container.innerHTML = upcoming.map(e => `
            <div class="event-item">
                <span class="event-emoji">${e.emoji}</span>
                <div class="event-info">
                    <div class="event-title">${e.title}</div>
                    <div class="event-date">${e.date} - ${e.country}</div>
                </div>
            </div>
        `).join('');
    }
}

async function loadStats() {
    const data = await apiGet('/api/stats');
    if (data.success) {
        const container = document.getElementById('community-stats');
        const s = data.stats;
        container.innerHTML = `
            <div class="stat-row"><span class="stat-label">Membres</span><span class="stat-value">${s.total_users}</span></div>
            <div class="stat-row"><span class="stat-label">Publications</span><span class="stat-value">${s.total_posts}</span></div>
            <div class="stat-row"><span class="stat-label">Groupes</span><span class="stat-value">${s.total_groups}</span></div>
            <div class="stat-row"><span class="stat-label">Actifs aujourd'hui</span><span class="stat-value">${s.active_today}</span></div>
        `;
    }
}

// ══════ BADGES & POLLING ══════

async function updateBadges() {
    const notifData = await apiGet('/api/notifications/unread-count');
    if (notifData.success) {
        setBadge('notif-badge', notifData.count);
        setBadge('sidebar-notif-badge', notifData.count);
    }

    const msgData = await apiGet('/api/messages/unread-count');
    if (msgData.success) {
        setBadge('msg-badge', msgData.count);
        setBadge('sidebar-msg-badge', msgData.count);
        setBadge('bottom-msg-badge', msgData.count);
    }
}

function setBadge(id, count) {
    const el = document.getElementById(id);
    if (!el) return;
    if (count > 0) {
        el.textContent = count > 99 ? '99+' : count;
        el.classList.remove('hidden');
    } else {
        el.classList.add('hidden');
    }
}

function startBadgePolling() {
    updateBadges();
    setInterval(updateBadges, 30000);
}

// ══════ IMAGE VIEWER ══════

function openImage(url) {
    const viewer = document.getElementById('image-viewer');
    document.getElementById('iv-image').src = url;
    viewer.classList.remove('hidden');
}

function closeImageViewer() {
    document.getElementById('image-viewer').classList.add('hidden');
}

// ══════ INITIALIZATION ══════

async function init() {
    if (token) {
        const data = await apiGet('/api/auth/me');
        if (data.success) {
            currentUser = data.user;
            showApp();
        } else {
            showLanding();
        }
    } else {
        showLanding();
    }
}

// Override submitPost to support group posts
const _origSubmitPost = submitPost;
window.submitPost = async function() {
    const content = document.getElementById('post-content').value.trim();
    const images = postImages.filter(i => i !== null);
    const visibility = document.getElementById('post-visibility').value;
    const groupId = window._groupPostId || null;

    if (!content && images.length === 0) {
        showToast('Ecrivez quelque chose ou ajoutez une image', 'error');
        return;
    }

    const btn = document.getElementById('submit-post-btn');
    btn.disabled = true;
    btn.textContent = 'Publication...';

    const data = await apiPost('/api/posts', {
        content,
        images,
        feeling: postFeeling,
        location: postLocation,
        visibility,
        group_id: groupId
    });

    btn.disabled = false;
    btn.textContent = 'Publier';
    window._groupPostId = null;

    if (data.success) {
        closePostModal();
        showToast('Publication creee !', 'success');
        if (groupId) {
            loadGroupDetail(groupId);
        } else {
            loadFeed(true);
        }
    } else {
        showToast(data.error || 'Erreur', 'error');
    }
};

// Start the app
init();
