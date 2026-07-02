const API_BASE = '/api';
let notes = [];
let categories = [];
let tags = [];
let currentView = 'grid';
let currentCategory = '';
let currentTag = '';
let confirmCallback = null;

async function fetchNotes() {
    const search = document.getElementById('searchInput').value;
    const showArchived = document.getElementById('showArchived').checked;
    const showFavorites = document.getElementById('showFavorites').checked;
    
    let url = `${API_BASE}/notes?search=${encodeURIComponent(search)}`;
    
    if (currentCategory) {
        url += `&category_id=${currentCategory}`;
    }
    if (currentTag) {
        url += `&tag_id=${currentTag}`;
    }
    if (!showArchived) {
        url += '&is_archived=0';
    }
    if (showFavorites) {
        url += '&is_favorite=1';
    }
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        notes = data.notes || [];
        renderNotes();
        updateCategoryCounts();
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

async function fetchCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const data = await response.json();
        categories = data.categories || [];
        renderCategories();
        updateCategorySelect();
    } catch (error) {
        console.error('Error fetching categories:', error);
    }
}

async function fetchTags() {
    try {
        const response = await fetch(`${API_BASE}/tags`);
        const data = await response.json();
        tags = data.tags || [];
        renderTags();
    } catch (error) {
        console.error('Error fetching tags:', error);
    }
}

function renderNotes() {
    const noteList = document.getElementById('noteList');
    
    if (notes.length === 0) {
        noteList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-file-alt"></i>
                <p>暂无笔记</p>
            </div>
        `;
        return;
    }
    
    noteList.innerHTML = notes.map(note => {
        const categoryColor = note.category_color || '#999';
        const tagsHtml = note.tags ? note.tags.map(tag => 
            `<span class="note-tag">${tag.name}</span>`
        ).join('') : '';
        
        return `
            <div class="note-card ${note.is_archived ? 'archived' : ''} ${note.is_favorite ? 'favorite' : ''} ${note.category_id ? 'has-category' : ''}"
                 style="border-left-color: ${note.is_favorite ? '#ffc107' : (note.category_id ? categoryColor : '#e0e0e0')}"
                 onclick="editNote(${note.id})">
                <div class="note-header">
                    <h3 class="note-title">${escapeHtml(note.title)}</h3>
                    <div class="note-actions">
                        <button class="note-action-btn ${note.is_favorite ? 'favorite-btn' : ''}" 
                                onclick="event.stopPropagation(); toggleFavorite(${note.id})"
                                title="${note.is_favorite ? '取消收藏' : '收藏'}">
                            <i class="fas ${note.is_favorite ? 'fa-star' : 'fa-star-o'}"></i>
                        </button>
                        <button class="note-action-btn archive-btn" 
                                onclick="event.stopPropagation(); toggleArchive(${note.id})"
                                title="${note.is_archived ? '取消归档' : '归档'}">
                            <i class="fas ${note.is_archived ? 'fa-archive' : 'fa-archive'}"></i>
                        </button>
                        <button class="note-action-btn delete-btn" 
                                onclick="event.stopPropagation(); confirmDeleteNote(${note.id})"
                                title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <p class="note-content">${escapeHtml(note.content || '')}</p>
                <div class="note-meta">
                    ${note.category_id ? `<span class="note-category" style="background-color: ${categoryColor}20; color: ${categoryColor}">${note.category_name}</span>` : ''}
                    <div class="note-tags">${tagsHtml}</div>
                    <div class="note-stats">
                        <button class="stat-btn ${note.is_liked ? 'liked' : ''}" onclick="event.stopPropagation(); toggleNoteLike(${note.id})">
                            <i class="fas fa-heart"></i>
                            <span>${note.like_count || 0}</span>
                        </button>
                        <button class="stat-btn" onclick="event.stopPropagation(); openNoteDetail(${note.id})">
                            <i class="fas fa-comment"></i>
                            <span>${note.comment_count || 0}</span>
                        </button>
                    </div>
                    <span class="note-time">${formatTime(note.updated_at)}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderCategories() {
    const categoryList = document.getElementById('categoryList');
    const allItem = categoryList.querySelector('[data-id=""]');
    
    const items = categories.map(cat => `
        <div class="category-item ${currentCategory === cat.id.toString() ? 'active' : ''}" 
             data-id="${cat.id}" onclick="filterByCategory('${cat.id}')">
            <span class="category-dot" style="background-color: ${cat.color}"></span>
            <span>${cat.name}</span>
            <span class="category-count" id="count-${cat.id}">0</span>
        </div>
    `).join('');
    
    categoryList.innerHTML = allItem.outerHTML + items;
}

function renderTags() {
    const tagList = document.getElementById('tagList');
    const allItem = tagList.querySelector('[data-id=""]');
    
    const items = tags.map(tag => `
        <span class="tag-item ${currentTag === tag.id.toString() ? 'active' : ''}" 
              data-id="${tag.id}" onclick="filterByTag('${tag.id}')">${tag.name}</span>
    `).join('');
    
    tagList.innerHTML = allItem.outerHTML + items;
}

function updateCategorySelect() {
    const select = document.getElementById('noteCategory');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">未分类</option>' + 
        categories.map(cat => `
            <option value="${cat.id}" style="color: ${cat.color}">${cat.name}</option>
        `).join('');
    
    select.value = currentValue;
}

function updateCategoryCounts() {
    const counts = {};
    notes.forEach(note => {
        if (note.category_id) {
            counts[note.category_id] = (counts[note.category_id] || 0) + 1;
        }
    });
    
    categories.forEach(cat => {
        const el = document.getElementById(`count-${cat.id}`);
        if (el) {
            el.textContent = counts[cat.id] || 0;
        }
    });
    
    const allCount = document.querySelector('.category-item[data-id=""] .category-count');
    if (allCount) {
        allCount.textContent = notes.length;
    }
}

function filterByCategory(categoryId) {
    currentCategory = categoryId;
    document.querySelectorAll('.category-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === categoryId);
    });
    fetchNotes();
}

function filterByTag(tagId) {
    currentTag = tagId;
    document.querySelectorAll('.tag-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === tagId);
    });
    fetchNotes();
}

function handleSearch() {
    fetchNotes();
}

function handleFilterChange() {
    fetchNotes();
}

function switchView(view) {
    currentView = view;
    const noteList = document.getElementById('noteList');
    document.getElementById('gridViewBtn').classList.toggle('active', view === 'grid');
    document.getElementById('listViewBtn').classList.toggle('active', view === 'list');
    noteList.classList.toggle('grid-view', view === 'grid');
    noteList.classList.toggle('list-view', view === 'list');
}

function openNoteForm(noteId = null) {
    const modal = document.getElementById('noteModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('noteForm');
    
    if (noteId) {
        const note = notes.find(n => n.id === noteId);
        if (note) {
            modalTitle.textContent = '编辑笔记';
            document.getElementById('noteId').value = note.id;
            document.getElementById('noteTitle').value = note.title;
            document.getElementById('noteContent').value = note.content || '';
            document.getElementById('noteCategory').value = note.category_id || '';
            document.getElementById('noteTags').value = note.tags ? note.tags.map(t => t.name).join(', ') : '';
            document.getElementById('noteFavorite').checked = note.is_favorite === 1;
        }
    } else {
        modalTitle.textContent = '新建笔记';
        form.reset();
        document.getElementById('noteId').value = '';
    }
    
    modal.classList.add('active');
}

function closeNoteModal() {
    document.getElementById('noteModal').classList.remove('active');
}

function editNote(noteId) {
    openNoteForm(noteId);
}

async function saveNote(e) {
    e.preventDefault();
    
    const noteId = document.getElementById('noteId').value;
    const title = document.getElementById('noteTitle').value;
    const content = document.getElementById('noteContent').value;
    const categoryId = document.getElementById('noteCategory').value;
    const tagsInput = document.getElementById('noteTags').value;
    const isFavorite = document.getElementById('noteFavorite').checked ? 1 : 0;
    
    const tags = tagsInput.split(/[,，]/).map(t => t.trim()).filter(t => t);
    
    const data = {
        title,
        content,
        category_id: categoryId || null,
        tags,
        is_favorite: isFavorite
    };
    
    try {
        let response;
        if (noteId) {
            response = await fetch(`${API_BASE}/notes/${noteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch(`${API_BASE}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            closeNoteModal();
            await fetchNotes();
            await fetchTags();
        }
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

async function toggleFavorite(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (note) {
        try {
            await fetch(`${API_BASE}/notes/${noteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_favorite: note.is_favorite ? 0 : 1 })
            });
            await fetchNotes();
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    }
}

async function toggleArchive(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (note) {
        try {
            await fetch(`${API_BASE}/notes/${noteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_archived: note.is_archived ? 0 : 1 })
            });
            await fetchNotes();
        } catch (error) {
            console.error('Error toggling archive:', error);
        }
    }
}

function confirmDeleteNote(noteId) {
    confirmCallback = () => deleteNote(noteId);
    document.getElementById('confirmMessage').textContent = '确定要删除这条笔记吗？此操作无法撤销。';
    document.getElementById('confirmModal').classList.add('active');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('active');
    confirmCallback = null;
}

async function executeConfirm() {
    if (confirmCallback) {
        await confirmCallback();
    }
    closeConfirmModal();
}

async function deleteNote(noteId) {
    try {
        const response = await fetch(`${API_BASE}/notes/${noteId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await fetchNotes();
            await fetchTags();
        }
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

function toggleCategoryModal() {
    const modal = document.getElementById('categoryModal');
    if (modal.classList.contains('active')) {
        modal.classList.remove('active');
    } else {
        modal.classList.add('active');
        renderCategoryManageList();
    }
}

function renderCategoryManageList() {
    const list = document.getElementById('categoryManageList');
    list.innerHTML = categories.map(cat => `
        <div class="category-manage-item">
            <div class="category-info">
                <div class="category-color" style="background-color: ${cat.color}"></div>
                <span class="category-name">${cat.name}</span>
            </div>
            <div class="category-actions">
                <button class="category-action-btn" onclick="editCategory(${cat.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="category-action-btn delete" onclick="confirmDeleteCategory(${cat.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

async function addCategory() {
    const name = document.getElementById('newCategoryName').value;
    const color = document.getElementById('newCategoryColor').value;
    
    if (!name.trim()) {
        alert('请输入分类名称');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim(), color })
        });
        
        if (response.ok) {
            document.getElementById('newCategoryName').value = '';
            await fetchCategories();
            renderCategoryManageList();
        } else {
            const data = await response.json();
            alert(data.error || '添加失败');
        }
    } catch (error) {
        console.error('Error adding category:', error);
    }
}

function editCategory(categoryId) {
    const cat = categories.find(c => c.id === categoryId);
    if (cat) {
        const newName = prompt('请输入新的分类名称:', cat.name);
        if (newName && newName.trim()) {
            updateCategory(categoryId, { name: newName.trim() });
        }
    }
}

async function updateCategory(categoryId, data) {
    try {
        const response = await fetch(`${API_BASE}/categories/${categoryId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            await fetchCategories();
            renderCategoryManageList();
        } else {
            const res = await response.json();
            alert(res.error || '更新失败');
        }
    } catch (error) {
        console.error('Error updating category:', error);
    }
}

function confirmDeleteCategory(categoryId) {
    confirmCallback = () => deleteCategory(categoryId);
    document.getElementById('confirmMessage').textContent = '确定要删除这个分类吗？分类下的笔记将变为未分类。';
    document.getElementById('confirmModal').classList.add('active');
}

async function deleteCategory(categoryId) {
    try {
        const response = await fetch(`${API_BASE}/categories/${categoryId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await fetchCategories();
            renderCategoryManageList();
            if (currentCategory === categoryId.toString()) {
                filterByCategory('');
            }
        }
    } catch (error) {
        console.error('Error deleting category:', error);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
    
    return date.toLocaleDateString('zh-CN');
}

let currentDetailNoteId = null;
let commentsSort = 'time';

function toggleTagModal() {
    const modal = document.getElementById('tagModal');
    if (modal.classList.contains('active')) {
        modal.classList.remove('active');
    } else {
        modal.classList.add('active');
        renderTagManageList();
    }
}

function renderTagManageList() {
    const list = document.getElementById('tagManageList');
    const filterTags = tags.filter(t => t.name !== '全部');
    list.innerHTML = filterTags.map(tag => `
        <div class="tag-manage-item">
            <span class="tag-name">${tag.name}</span>
            <button class="tag-action-btn delete" onclick="confirmDeleteTag(${tag.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}

async function addTag() {
    const name = document.getElementById('newTagName').value;
    
    if (!name.trim()) {
        alert('请输入标签名称');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tags`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim() })
        });
        
        if (response.ok) {
            document.getElementById('newTagName').value = '';
            await fetchTags();
            renderTagManageList();
        } else {
            const data = await response.json();
            alert(data.error || '添加失败');
        }
    } catch (error) {
        console.error('Error adding tag:', error);
    }
}

function confirmDeleteTag(tagId) {
    confirmCallback = () => deleteTag(tagId);
    document.getElementById('confirmMessage').textContent = '确定要删除这个标签吗？相关笔记的该标签将被移除。';
    document.getElementById('confirmModal').classList.add('active');
}

async function deleteTag(tagId) {
    try {
        const response = await fetch(`${API_BASE}/tags/${tagId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await fetchTags();
            renderTagManageList();
            if (currentTag === tagId.toString()) {
                filterByTag('');
            }
        }
    } catch (error) {
        console.error('Error deleting tag:', error);
    }
}

async function openNoteDetail(noteId) {
    currentDetailNoteId = noteId;
    const modal = document.getElementById('noteDetailModal');
    modal.classList.add('active');
    
    try {
        const [noteRes, commentsRes, likeRes] = await Promise.all([
            fetch(`${API_BASE}/notes/${noteId}`),
            fetch(`${API_BASE}/notes/${noteId}/comments?sort=${commentsSort}`),
            fetch(`${API_BASE}/notes/${noteId}/like/status`)
        ]);
        
        const note = await noteRes.json();
        const commentsData = await commentsRes.json();
        const likeStatus = await likeRes.json();
        
        document.getElementById('detailTitle').textContent = note.title;
        document.getElementById('detailContent').textContent = note.content || '';
        document.getElementById('detailTime').textContent = formatTime(note.updated_at);
        
        document.getElementById('detailLikeCount').textContent = likeStatus.like_count || 0;
        document.getElementById('detailCommentCount').textContent = note.comment_count || 0;
        
        const likeBtn = document.getElementById('detailLikeBtn');
        if (likeStatus.is_liked) {
            likeBtn.classList.add('liked');
        } else {
            likeBtn.classList.remove('liked');
        }
        
        const tagsHtml = note.tags ? note.tags.map(tag => 
            `<span class="detail-tag">${tag.name}</span>`
        ).join('') : '';
        document.getElementById('detailTags').innerHTML = tagsHtml;
        
        document.getElementById('detailCategory').innerHTML = note.category_id 
            ? `<span class="detail-category-item" style="background-color: ${note.category_color}20; color: ${note.category_color}">${note.category_name}</span>` 
            : '';
        
        renderComments(commentsData.comments || []);
    } catch (error) {
        console.error('Error loading note detail:', error);
    }
}

function closeNoteDetail() {
    document.getElementById('noteDetailModal').classList.remove('active');
    currentDetailNoteId = null;
}

async function fetchComments() {
    if (!currentDetailNoteId) return;
    
    try {
        const response = await fetch(`${API_BASE}/notes/${currentDetailNoteId}/comments?sort=${commentsSort}`);
        const data = await response.json();
        renderComments(data.comments || []);
    } catch (error) {
        console.error('Error fetching comments:', error);
    }
}

function renderComments(comments) {
    const commentList = document.getElementById('commentList');
    
    if (comments.length === 0) {
        commentList.innerHTML = `
            <div class="empty-comments">
                <i class="fas fa-comments"></i>
                <p>暂无评论，快来发表第一条评论吧</p>
            </div>
        `;
        return;
    }
    
    commentList.innerHTML = comments.map(comment => {
        const repliesHtml = comment.replies ? comment.replies.map(reply => `
            <div class="comment-reply">
                <div class="reply-content">
                    <span class="reply-location">${reply.ip_location}</span>
                    <span class="reply-text">${escapeHtml(reply.content)}</span>
                    <span class="reply-time">${formatTime(reply.created_at)}</span>
                </div>
                <button class="reply-like-btn ${reply.is_liked ? 'liked' : ''}" onclick="toggleCommentLike(${reply.id}, this)">
                    <i class="fas fa-thumbs-up"></i>
                    <span>${reply.like_count || 0}</span>
                </button>
            </div>
        `).join('') : '';
        
        return `
            <div class="comment-item">
                <div class="comment-content">
                    <span class="comment-location">${comment.ip_location}</span>
                    <p>${escapeHtml(comment.content)}</p>
                    <span class="comment-time">${formatTime(comment.created_at)}</span>
                </div>
                <div class="comment-actions">
                    <button class="comment-action-btn ${comment.is_liked ? 'liked' : ''}" onclick="toggleCommentLike(${comment.id}, this)">
                        <i class="fas fa-thumbs-up"></i>
                        <span>${comment.like_count || 0}</span>
                    </button>
                    <button class="comment-action-btn reply-btn" onclick="replyToComment(${comment.id})">
                        <i class="fas fa-reply"></i>
                        <span>回复</span>
                    </button>
                </div>
                ${repliesHtml ? `<div class="comment-replies">${repliesHtml}</div>` : ''}
            </div>
        `;
    }).join('');
}

async function submitComment(parentId = null) {
    if (!currentDetailNoteId) return;
    
    const content = document.getElementById('commentInput').value;
    
    if (!content.trim()) {
        alert('请输入评论内容');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/notes/${currentDetailNoteId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                content: content.trim(),
                parent_id: parentId || null
            })
        });
        
        if (response.ok) {
            document.getElementById('commentInput').value = '';
            await fetchComments();
            await fetchNotes();
        } else {
            const data = await response.json();
            alert(data.error || '发表失败');
        }
    } catch (error) {
        console.error('Error submitting comment:', error);
    }
}

function replyToComment(parentId) {
    const input = document.getElementById('commentInput');
    input.placeholder = `回复评论...`;
    input.focus();
    const submitBtn = document.querySelector('.comment-submit-btn');
    submitBtn.onclick = () => submitComment(parentId);
}

function sortComments(sortBy) {
    commentsSort = sortBy;
    document.querySelectorAll('.sort-btn').forEach(el => {
        el.classList.toggle('active', el.textContent === (sortBy === 'time' ? '最新' : '最热'));
    });
    fetchComments();
}

async function toggleNoteLike(noteId) {
    try {
        const response = await fetch(`${API_BASE}/notes/${noteId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            await fetchNotes();
        }
    } catch (error) {
        console.error('Error toggling note like:', error);
    }
}

async function toggleNoteLikeFromDetail() {
    if (!currentDetailNoteId) return;
    
    try {
        const response = await fetch(`${API_BASE}/notes/${currentDetailNoteId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('detailLikeCount').textContent = data.like_count;
            
            const likeBtn = document.getElementById('detailLikeBtn');
            if (data.liked) {
                likeBtn.classList.add('liked');
            } else {
                likeBtn.classList.remove('liked');
            }
            
            await fetchNotes();
        }
    } catch (error) {
        console.error('Error toggling note like:', error);
    }
}

async function toggleCommentLike(commentId, btn) {
    try {
        const response = await fetch(`${API_BASE}/comments/${commentId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const countSpan = btn.querySelector('span');
            countSpan.textContent = data.like_count;
            
            if (data.liked) {
                btn.classList.add('liked');
            } else {
                btn.classList.remove('liked');
            }
        }
    } catch (error) {
        console.error('Error toggling comment like:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchNotes();
    fetchCategories();
    fetchTags();
});