/**
 * Infinite Story Web - Main JavaScript
 * 
 * Handles user interactions, story generation requests,
 * and real-time collaborative features.
 */

// Configuration
const CONFIG = {
    API_BASE_URL: window.location.origin,
    SCROLL_THRESHOLD: 100,
    INTERACTION_DEBOUNCE: 500,
    AUTO_SCROLL_ENABLED: true,
    TYPEWRITER_SPEED: 30,
};

// Application State
const state = {
    sessionId: null,
    userId: null,
    isLoading: false,
    storyStarted: false,
    lastInteractionTime: 0,
    scrollPosition: 0,
    socket: null,
    pendingMergeRequest: null,
};

// DOM Elements
const elements = {
    storyContainer: null,
    storyContent: null,
    storyLoading: null,
    genreSelect: null,
    moodSelect: null,
    newStoryBtn: null,
    mergeBtn: null,
    mergePanel: null,
    mergeList: null,
    closeMergeBtn: null,
    mergeNotification: null,
    acceptMergeBtn: null,
    rejectMergeBtn: null,
    contextGenre: null,
    contextMood: null,
    contextTension: null,
    contextLength: null,
};

/**
 * Initialize the application
 */
async function init() {
    // Cache DOM elements
    cacheElements();
    
    // Set up event listeners
    setupEventListeners();
    
    // Create session
    await createSession();
    
    // Initialize WebSocket connection
    initializeSocket();
    
    console.log('Infinite Story Web initialized');
}

/**
 * Cache DOM element references
 */
function cacheElements() {
    elements.storyContainer = document.getElementById('story-container');
    elements.storyContent = document.getElementById('story-content');
    elements.storyLoading = document.getElementById('story-loading');
    elements.genreSelect = document.getElementById('genre-select');
    elements.moodSelect = document.getElementById('mood-select');
    elements.newStoryBtn = document.getElementById('new-story-btn');
    elements.mergeBtn = document.getElementById('merge-btn');
    elements.mergePanel = document.getElementById('merge-panel');
    elements.mergeList = document.getElementById('merge-list');
    elements.closeMergeBtn = document.getElementById('close-merge-btn');
    elements.mergeNotification = document.getElementById('merge-notification');
    elements.acceptMergeBtn = document.getElementById('accept-merge-btn');
    elements.rejectMergeBtn = document.getElementById('reject-merge-btn');
    elements.contextGenre = document.getElementById('context-genre');
    elements.contextMood = document.getElementById('context-mood');
    elements.contextTension = document.getElementById('context-tension');
    elements.contextLength = document.getElementById('context-length');
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Button clicks
    elements.newStoryBtn.addEventListener('click', startNewStory);
    elements.mergeBtn.addEventListener('click', showMergePanel);
    elements.closeMergeBtn.addEventListener('click', hideMergePanel);
    elements.acceptMergeBtn.addEventListener('click', acceptMerge);
    elements.rejectMergeBtn.addEventListener('click', rejectMerge);
    
    // Select changes
    elements.genreSelect.addEventListener('change', handleGenreChange);
    elements.moodSelect.addEventListener('change', handleMoodChange);
    
    // Story container interactions
    elements.storyContainer.addEventListener('scroll', debounce(handleScroll, CONFIG.INTERACTION_DEBOUNCE));
    elements.storyContainer.addEventListener('click', handleClick);
    
    // Document-level events
    document.addEventListener('keydown', handleKeypress);
}

/**
 * Create a new session with the server
 */
async function createSession() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        state.sessionId = data.session_id;
        state.userId = data.user_id;
        
        console.log('Session created:', state.sessionId);
    } catch (error) {
        console.error('Failed to create session:', error);
        showError('Failed to connect to server. Please refresh the page.');
    }
}

/**
 * Initialize WebSocket connection for real-time features
 */
function initializeSocket() {
    if (typeof io === 'undefined') {
        console.warn('Socket.IO not available, real-time features disabled');
        return;
    }
    
    state.socket = io(CONFIG.API_BASE_URL);
    
    state.socket.on('connect', () => {
        console.log('WebSocket connected');
        if (state.sessionId) {
            state.socket.emit('join_story', { session_id: state.sessionId });
        }
    });
    
    state.socket.on('story_update', (data) => {
        if (data.segment) {
            appendStorySegment(data.segment.content, data.segment.is_merged);
        }
        if (data.context) {
            updateContextDisplay(data.context);
        }
    });
    
    state.socket.on('merge_request', (data) => {
        state.pendingMergeRequest = data;
        showMergeNotification();
    });
    
    state.socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

/**
 * Start a new story
 */
async function startNewStory() {
    if (state.isLoading) return;
    
    state.isLoading = true;
    showLoading(true);
    
    // Clear existing story
    elements.storyContent.innerHTML = '';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/story/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId })
        });
        
        const data = await response.json();
        
        if (data.segment) {
            appendStorySegment(data.segment.content, false, true);
            state.storyStarted = true;
        }
        
        if (data.context) {
            updateContextDisplay(data.context);
        }
    } catch (error) {
        console.error('Failed to start story:', error);
        showError('Failed to start story. Please try again.');
    } finally {
        state.isLoading = false;
        showLoading(false);
    }
}

/**
 * Continue the story with a new segment
 */
async function continueStory(interaction) {
    if (state.isLoading || !state.storyStarted) return;
    
    state.isLoading = true;
    showLoading(true);
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/story/continue`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                interaction: interaction
            })
        });
        
        const data = await response.json();
        
        if (data.segment) {
            appendStorySegment(data.segment.content, data.segment.is_merged);
        }
        
        if (data.context) {
            updateContextDisplay(data.context);
        }
    } catch (error) {
        console.error('Failed to continue story:', error);
    } finally {
        state.isLoading = false;
        showLoading(false);
    }
}

/**
 * Append a new story segment to the display
 */
function appendStorySegment(content, isMerged = false, isFirst = false) {
    const segment = document.createElement('span');
    segment.className = 'story-segment';
    if (isMerged) {
        segment.classList.add('merged');
    }
    
    // Add space before segment (except first)
    if (!isFirst && elements.storyContent.textContent.trim()) {
        segment.textContent = ' ' + content;
    } else {
        segment.textContent = content;
    }
    
    elements.storyContent.appendChild(segment);
    
    // Auto-scroll to bottom
    if (CONFIG.AUTO_SCROLL_ENABLED) {
        elements.storyContainer.scrollTop = elements.storyContainer.scrollHeight;
    }
}

/**
 * Update the context display
 */
function updateContextDisplay(context) {
    if (context.genre) {
        elements.contextGenre.textContent = `Genre: ${capitalize(context.genre)}`;
    }
    if (context.mood) {
        elements.contextMood.textContent = `Mood: ${capitalize(context.mood)}`;
    }
    if (context.tension_level !== undefined) {
        const tensionPercent = Math.round(context.tension_level * 100);
        elements.contextTension.textContent = `Tension: ${tensionPercent}%`;
    }
    if (context.story_length !== undefined) {
        elements.contextLength.textContent = `Words: ${context.story_length}`;
    }
}

/**
 * Handle scroll interaction
 */
function handleScroll(event) {
    if (!state.storyStarted) return;
    
    const container = elements.storyContainer;
    const scrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    
    // Check if scrolled near bottom
    if (scrollTop + clientHeight >= scrollHeight - CONFIG.SCROLL_THRESHOLD) {
        const now = Date.now();
        if (now - state.lastInteractionTime > CONFIG.INTERACTION_DEBOUNCE) {
            state.lastInteractionTime = now;
            continueStory({
                type: 'scroll',
                amount: scrollTop - state.scrollPosition
            });
        }
    }
    
    state.scrollPosition = scrollTop;
}

/**
 * Handle click interaction
 */
function handleClick(event) {
    if (!state.storyStarted) return;
    
    const now = Date.now();
    if (now - state.lastInteractionTime > CONFIG.INTERACTION_DEBOUNCE) {
        state.lastInteractionTime = now;
        
        // Get click position relative to container
        const rect = elements.storyContainer.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        continueStory({
            type: 'click',
            x: x,
            y: y
        });
    }
}

/**
 * Handle keypress interaction
 */
function handleKeypress(event) {
    if (!state.storyStarted) return;
    
    // Ignore if typing in input/select
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT') {
        return;
    }
    
    const now = Date.now();
    if (now - state.lastInteractionTime > CONFIG.INTERACTION_DEBOUNCE) {
        state.lastInteractionTime = now;
        
        continueStory({
            type: 'keypress',
            key: event.key,
            code: event.code
        });
    }
}

/**
 * Handle genre selection change
 */
async function handleGenreChange(event) {
    if (!state.storyStarted) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/story/genre`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                genre: event.target.value
            })
        });
        
        const data = await response.json();
        if (data.context) {
            updateContextDisplay(data.context);
        }
    } catch (error) {
        console.error('Failed to set genre:', error);
    }
}

/**
 * Handle mood selection change
 */
async function handleMoodChange(event) {
    if (!state.storyStarted) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/story/mood`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                mood: event.target.value
            })
        });
        
        const data = await response.json();
        if (data.context) {
            updateContextDisplay(data.context);
        }
    } catch (error) {
        console.error('Failed to set mood:', error);
    }
}

/**
 * Show the merge panel with available storylines
 */
async function showMergePanel() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/active`);
        const data = await response.json();
        
        elements.mergeList.innerHTML = '';
        
        if (data.users && data.users.length > 1) {
            // Filter out current user
            const otherUsers = data.users.filter(u => u.session_id !== state.sessionId);
            
            if (otherUsers.length > 0) {
                otherUsers.forEach(user => {
                    const item = createMergeItem(user);
                    elements.mergeList.appendChild(item);
                });
            } else {
                elements.mergeList.innerHTML = '<p class="no-storylines">No other storylines available</p>';
            }
        } else {
            elements.mergeList.innerHTML = '<p class="no-storylines">No other storylines available</p>';
        }
        
        elements.mergePanel.classList.remove('hidden');
    } catch (error) {
        console.error('Failed to fetch active users:', error);
    }
}

/**
 * Create a merge item element
 */
function createMergeItem(user) {
    const item = document.createElement('div');
    item.className = 'merge-item';
    
    const info = document.createElement('div');
    info.className = 'merge-item-info';
    info.textContent = `Story #${user.session_id.substring(0, 8)}...`;
    
    const btn = document.createElement('button');
    btn.className = 'control-btn primary';
    btn.textContent = 'Merge';
    btn.addEventListener('click', () => requestMerge(user.session_id));
    
    item.appendChild(info);
    item.appendChild(btn);
    
    return item;
}

/**
 * Hide the merge panel
 */
function hideMergePanel() {
    elements.mergePanel.classList.add('hidden');
}

/**
 * Request a merge with another user's storyline
 */
async function requestMerge(targetSessionId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/merge/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                target_session_id: targetSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.merge_request) {
            hideMergePanel();
            alert('Merge request sent!');
        }
    } catch (error) {
        console.error('Failed to request merge:', error);
    }
}

/**
 * Show merge notification
 */
function showMergeNotification() {
    elements.mergeNotification.classList.remove('hidden');
}

/**
 * Hide merge notification
 */
function hideMergeNotification() {
    elements.mergeNotification.classList.add('hidden');
    state.pendingMergeRequest = null;
}

/**
 * Accept a merge request
 */
async function acceptMerge() {
    if (!state.pendingMergeRequest) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/merge/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                request_id: state.pendingMergeRequest.request_id
            })
        });
        
        const data = await response.json();
        
        if (data.segment) {
            appendStorySegment(data.segment.content, true);
        }
        
        if (data.context) {
            updateContextDisplay(data.context);
        }
        
        hideMergeNotification();
    } catch (error) {
        console.error('Failed to accept merge:', error);
    }
}

/**
 * Reject a merge request
 */
function rejectMerge() {
    hideMergeNotification();
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    if (show) {
        elements.storyLoading.classList.add('active');
    } else {
        elements.storyLoading.classList.remove('active');
    }
}

/**
 * Show an error message
 */
function showError(message) {
    // Simple alert for now, could be enhanced with custom modal
    alert(message);
}

/**
 * Utility: Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility: Capitalize first letter
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        state,
        init,
        createSession,
        startNewStory,
        continueStory,
        appendStorySegment,
        updateContextDisplay,
        handleScroll,
        handleClick,
        handleKeypress,
        debounce,
        capitalize
    };
}
