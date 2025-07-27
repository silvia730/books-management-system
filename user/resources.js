// API Base URL
let API_BASE = 'https://books-management-system-bcr5.onrender.com/api';

// User authentication state
let currentUser = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    setupEventListeners();
});

function initializePage() {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const selectedClass = urlParams.get('class');
    const selectedSubject = urlParams.get('subject');
    
    // Update filter info
    updateFilterInfo(selectedClass, selectedSubject);
    
    // Load and display resources
    loadFilteredResources(selectedClass, selectedSubject);
    
    // Check if user is logged in
    checkUserAuth();
}

function updateFilterInfo(selectedClass, selectedSubject) {
    const filterInfo = document.getElementById('filter-info');
    if (filterInfo) {
        filterInfo.innerHTML = `
            <h3>Showing resources for:</h3>
            <p><strong>Class:</strong> ${selectedClass || 'All'} | <strong>Subject:</strong> ${selectedSubject || 'All'}</p>
        `;
    }
}

function loadFilteredResources(selectedClass, selectedSubject) {
    const resourcesContent = document.getElementById('resources-content');
    resourcesContent.innerHTML = '<div class="loading">Loading resources...</div>';
    
    // Fetch all resources from the API with filters
    const url = new URL(`${API_BASE}/resources`);
    if (selectedClass) url.searchParams.append('class', selectedClass);
    if (selectedSubject) url.searchParams.append('subject', selectedSubject);
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            // Use the filtered data directly from the API
            const filteredResources = data.all || [];
            displayResources(filteredResources);
        })
        .catch(error => {
            console.error('Failed to fetch resources:', error);
            resourcesContent.innerHTML = '<div class="no-resources">Failed to load resources. Please try again.</div>';
        });
}



function displayResources(resources) {
    const resourcesContent = document.getElementById('resources-content');
    
    if (!resources || resources.length === 0) {
        resourcesContent.innerHTML = `
            <div class="no-resources">
                <h3>No resources found</h3>
                <p>No resources available for the selected class and subject combination.</p>
                <a href="index.html" class="btn btn-primary">Back to Home</a>
            </div>
        `;
        return;
    }
    
    const resourcesGrid = document.createElement('div');
    resourcesGrid.className = 'resources-grid';
    
    resources.forEach(resource => {
        const resourceCard = createResourceCard(resource);
        resourcesGrid.appendChild(resourceCard);
    });
    
    resourcesContent.innerHTML = '';
    resourcesContent.appendChild(resourcesGrid);
}

function createResourceCard(resource) {
    const card = document.createElement('div');
    card.className = 'resource-card';
    
    // Use a default image if cover is missing
    let coverUrl = resource.cover && resource.cover !== 'null' ? resource.cover : 'assets/placeholder.jpg';
    if (resource.cover && resource.cover.startsWith('static/covers/')) {
        const baseUrl = API_BASE.replace('/api', '');
        coverUrl = `${baseUrl}/${resource.cover}`;
    }
    
    card.innerHTML = `
        <div class="resource-cover" style="background-image: url('${coverUrl}')"></div>
        <div class="resource-info">
            <div class="resource-type">${resource.resource_type || 'Resource'}</div>
            <h3 class="resource-title">${resource.title}</h3>
            <p class="resource-description">${resource.description || 'No description available'}</p>
            <div class="resource-meta">
                <div class="resource-price">Ksh 100</div>
                <div class="resource-details">
                    <small>Class: ${resource.class_grade || 'N/A'}</small><br>
                    <small>Subject: ${resource.subject || 'N/A'}</small>
                </div>
            </div>
            <button class="download-btn" data-resource-id="${resource.id}">Download</button>
        </div>
    `;
    
    // Add click event for download button
    const downloadBtn = card.querySelector('.download-btn');
    downloadBtn.addEventListener('click', () => {
        handleDownloadClick(resource);
    });
    
    return card;
}

function handleDownloadClick(resource) {
    // Check if user is logged in
    if (!currentUser) {
        alert('Please sign in to download resources.');
        openModal(document.getElementById('signin-modal'));
        return;
    }
    
    // Open download modal
    openModal(document.getElementById('download-modal'));
    
    // Pre-fill form with user data if available
    if (currentUser) {
        document.getElementById('download-name').value = currentUser.username || '';
        document.getElementById('download-email').value = currentUser.email || '';
    }
    
    // Store current resource ID
    window.currentDownloadResourceId = resource.id;
}

function setupEventListeners() {
    // Modal close buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) closeModal(modal);
        });
    });
    
    // Download form submission
    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
        downloadForm.addEventListener('submit', handleDownloadSubmit);
    }
    
    // Sign in form
    const signinForm = document.getElementById('signin-form');
    if (signinForm) {
        signinForm.addEventListener('submit', handleSignIn);
    }
    
    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });
}

function handleDownloadSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('download-name').value;
    const email = document.getElementById('download-email').value;
    const phone = document.getElementById('download-phone').value;
    
    if (!name || !email || !phone) {
        showDownloadMessage('Please fill in all fields.', 'error');
        return;
    }
    
    if (!window.currentDownloadResourceId) {
        showDownloadMessage('No resource selected.', 'error');
        return;
    }
    
    showDownloadMessage('Processing payment...', 'info');
    
    // Submit payment request
    fetch(`${API_BASE}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            resource_id: window.currentDownloadResourceId,
            email: email,
            amount: 100,
            name: name,
            phone: phone
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.message && data.message.includes('Test payment')) {
            // Test payment successful
            showDownloadMessage(`
                <div style="color: green;">✅ ${data.message}</div>
                <a href="download-success.html?resource_id=${encodeURIComponent(window.currentDownloadResourceId)}&email=${encodeURIComponent(email)}&orderTrackingId=${encodeURIComponent(data.orderTrackingId)}" target="_blank" class="btn btn-primary">Download Now</a>
            `, 'success');
        } else if (data.payment_url) {
            // PesaPal payment
            window.open(data.payment_url, '_blank');
            showDownloadMessage(`
                Payment page opened in new tab. After completing payment, 
                <a href="download-success.html?resource_id=${encodeURIComponent(window.currentDownloadResourceId)}&email=${encodeURIComponent(email)}&orderTrackingId=${encodeURIComponent(data.orderTrackingId)}" target="_blank">click here to download</a>.
            `, 'info');
        } else {
            showDownloadMessage(data.error || 'Failed to initiate payment.', 'error');
        }
    })
    .catch(error => {
        console.error('Payment error:', error);
        showDownloadMessage('Failed to connect to payment service.', 'error');
    });
}

function handleSignIn(e) {
    e.preventDefault();
    
    const username = document.getElementById('signin-username').value;
    const password = document.getElementById('signin-password').value;
    
    fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateAuthUI();
            closeModal(document.getElementById('signin-modal'));
            alert('Sign in successful!');
        } else {
            alert(data.error || 'Sign in failed');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        alert('Failed to connect to server.');
    });
}

function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Registration successful! You can now sign in.');
            closeModal(document.getElementById('register-modal'));
            // Switch to sign in modal
            openModal(document.getElementById('signin-modal'));
        } else {
            alert(data.error || 'Registration failed');
        }
    })
    .catch(error => {
        console.error('Register error:', error);
        alert('Failed to connect to server.');
    });
}

function checkUserAuth() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            updateAuthUI();
        } catch (error) {
            console.error('Error parsing saved user:', error);
            localStorage.removeItem('currentUser');
        }
    }
}

function updateAuthUI() {
    const authButtons = document.querySelector('.auth-buttons');
    if (authButtons) {
        if (currentUser) {
            authButtons.innerHTML = `
                <span>Welcome, ${currentUser.username}</span>
                <button class="btn btn-outline" onclick="signOut()">Sign Out</button>
            `;
        } else {
            authButtons.innerHTML = `
                <button class="btn btn-outline" onclick="openModal(document.getElementById('signin-modal'))">
                    <i class="fas fa-user"></i> Sign In
                </button>
                <button class="btn btn-primary" onclick="openModal(document.getElementById('register-modal'))">
                    Register
                </button>
            `;
        }
    }
}

function signOut() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    updateAuthUI();
    alert('Signed out successfully!');
}

function showDownloadMessage(message, type = 'info') {
    const messageDiv = document.getElementById('download-modal-message');
    if (messageDiv) {
        messageDiv.innerHTML = message;
        messageDiv.className = `message ${type}`;
    }
}

function openModal(modal) {
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modal) {
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        
        // Reset download form if closing download modal
        if (modal.id === 'download-modal') {
            const form = document.getElementById('download-form');
            if (form) form.reset();
            showDownloadMessage('');
            window.currentDownloadResourceId = null;
        }
    }
} 