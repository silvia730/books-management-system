// Revision Papers Data
const revisionPapers = [
    { 
        image: "assets/exam paper2.jpg"
    },
    { 
        image: "assets/WhatsApp Image 2025-07-21 at 17.39.48_efa085dc.jpg"
    },
    { 
        image: "assets/exam paper2.jpg"
    }
];

// Add this helper at the top for robust null/undefined checks
function isNullOrEmpty(val) {
    return val === null || val === undefined || val === '';
}

// Add these at the top of the file, outside any function:
let currentDownloadResourceId = null;
let downloadFormData = null;
let API_BASE = 'https://books-management-system-bcr5.onrender.com/api';
let currentUser = null; // Add user authentication state

function fetchApiBaseUrl() {
    // API_BASE is already set at the top of the file
    console.log('API Base URL set to:', API_BASE);
    // Return a resolved promise to ensure initialization continues
    return Promise.resolve(API_BASE);
}

// Add this function near the top
function resetDownloadState() {
    currentDownloadResourceId = null;
    downloadFormData = null;
    // Optionally reset form fields and messages
    const form = document.getElementById('download-form');
    if (form) form.reset();
    const msg = document.getElementById('download-modal-message');
    if (msg) msg.textContent = '';
    const pesapalBtn = document.getElementById('download-pesapal-btn');
    if (pesapalBtn) {
        pesapalBtn.style.display = 'none';
        pesapalBtn.disabled = true;
    }
}

// 1. Data for resources
// Replace resources object and all renderGeneralResources calls with API fetches
// Example for books:
function fetchAndRenderResources() {
    if (!API_BASE) {
        console.warn('API_BASE not loaded yet, skipping resource fetch');
        return;
    }
    
    console.log('🔄 Fetching resources from:', `${API_BASE}/resources`);
    
    fetch(`${API_BASE}/resources`, {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
        .then(res => {
            console.log('📡 Response status:', res.status);
            return res.json();
        })
        .then(data => {
            console.log('📚 Received data:', data);
            console.log('📖 Books count:', data.books?.length || 0);
            console.log('📄 Papers count:', data.papers?.length || 0);
            console.log('📚 Setbooks count:', data.setbooks?.length || 0);
            
            renderGeneralResources('.books-section', data.books || getSampleBooks(), 'general');
            renderGeneralResources('#papers', data.papers || getSamplePapers(), 'paper');
            renderGeneralResources('#setbooks', data.setbooks || getSampleSetbooks(), 'setbook');
        })
        .catch((error) => {
            console.error('❌ Failed to fetch resources:', error);
            renderGeneralResources('.books-section', getSampleBooks(), 'general');
            renderGeneralResources('#papers', getSamplePapers(), 'paper');
            renderGeneralResources('#setbooks', getSampleSetbooks(), 'setbook');
        });
}

// Sample data for demonstration
function getSampleBooks() {
    return [
        {
            id: '1',
            title: 'Form 2',
            description: 'Comprehensive guide covering algebra, geometry, and statistics for secondary students.',
            cover: 'assets/placeholder.jpg',
            grade: 'Form 2',
            subject: 'Mathematics'
        },
        {
            id: '2',
            title: 'Science Explorer',
            description: 'Interactive science textbook with experiments and activities for primary students.',
            cover: 'assets/placeholder.jpg',
            grade: 'Standard 7',
            subject: 'Science'
        },
        {
            id: '3',
            title: 'CBC Life Skills',
            description: 'Essential life skills curriculum for Competency Based Curriculum implementation.',
            cover: 'assets/placeholder.jpg',
            grade: 'Grade 5',
            subject: 'Life Skills'
        }
    ];
}

function getSamplePapers() {
    return [
        {
            id: '4',
            title: 'KCPE Mathematics 2023',
            description: 'Complete KCPE Mathematics past paper with marking scheme.',
            cover: 'assets/exam paper2.jpg',
            grade: 'Standard 8',
            subject: 'Mathematics'
        },
        {
            id: '5',
            title: 'KCSE English 2023',
            description: 'KCSE English paper with comprehensive answers.',
            cover: 'assets/placeholder.jpg',
            grade: 'Form 4',
            subject: 'English'
        }
    ];
}

function getSampleSetbooks() {
    return [
        {
            id: '6',
            title: 'The River and the Source',
            description: 'Classic Kenyan literature for secondary school students.',
            cover: 'assets/placeholder.jpg',
            grade: 'Form 3',
            subject: 'Literature'
        },
        {
            id: '7',
            title: 'A Doll\'s House',
            description: 'Modern drama text for advanced literature studies.',
            cover: 'assets/placeholder.jpg',
            grade: 'Form 4',
            subject: 'Literature'
        }
    ];
}

// Initialize the revision papers slider
function initRevisionSlider() {
    const sliderContainer = document.querySelector('.slider-container');
    const sliderNav = document.querySelector('.slider-nav');
    
    if (!sliderContainer || !sliderNav) {
        console.log('Slider elements not found, skipping slider initialization');
        return;
    }
    
    // Clear existing content
    sliderContainer.innerHTML = '';
    sliderNav.innerHTML = '';
    
            // Add slides to the slider
        revisionPapers.forEach((paper, index) => {
            // Create slider item
            const sliderItem = document.createElement('div');
            sliderItem.className = 'slider-item';
            sliderItem.innerHTML = `
                <img src="${paper.image}" alt="Educational Resource" class="slider-image">
            `;
            sliderContainer.appendChild(sliderItem);
            
            // Create navigation dot
            const dot = document.createElement('div');
            dot.className = 'slider-dot';
            dot.dataset.index = index;
            if (index === 0) dot.classList.add('active');
            sliderNav.appendChild(dot);
        });
    
    // Set up slider navigation
    setupSliderNavigation();
}

// Set up slider navigation and controls
function setupSliderNavigation() {
    const slider = document.querySelector('.slider-container');
    const dots = document.querySelectorAll('.slider-dot');
    const prevBtn = document.querySelector('.slider-arrow.prev');
    const nextBtn = document.querySelector('.slider-arrow.next');
    let currentSlide = 0;
    const slideCount = revisionPapers.length;
    
    // Function to go to a specific slide
    function goToSlide(index) {
        currentSlide = index;
        slider.style.transform = `translateX(-${currentSlide * 100}%)`;
        
        // Update active dot
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === currentSlide);
        });
    }
    
    // Next slide
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slideCount;
        goToSlide(currentSlide);
    }
    
    // Previous slide
    function prevSlide() {
        currentSlide = (currentSlide - 1 + slideCount) % slideCount;
        goToSlide(currentSlide);
    }
    
    // Event listeners
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);
    
    // Dot navigation
    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            goToSlide(parseInt(dot.dataset.index));
        });
    });
    
    // Auto slide
    let autoSlide = setInterval(nextSlide, 5000);
    
    // Pause on hover
    const sliderContainer = document.querySelector('.revision-slider');
    sliderContainer.addEventListener('mouseenter', () => {
        clearInterval(autoSlide);
    });
    
    sliderContainer.addEventListener('mouseleave', () => {
        autoSlide = setInterval(nextSlide, 5000);
    });
}

// Render General Books, Papers, Setbooks
function renderGeneralResources(sectionSelector, items, type) {
    const section = document.querySelector(sectionSelector);
    if (!section) return;
    const grid = section.querySelector('.books-grid');
    if (!grid) return;
    grid.innerHTML = '';
    if (!items.length) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; color:#888;">No resources found in this category.</div>';
        return;
    }
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = `book-card ${type}`;
        card.setAttribute('data-id', item.id || '');
        
        // Use a default image if cover is missing/null
        let coverUrl = 'assets/placeholder.jpg'; // Default fallback
        
        if (item.cover && item.cover !== 'null') {
            if (item.cover.startsWith('static/covers/')) {
                // Use the deployed API base URL for static files
                const baseUrl = API_BASE.replace('/api', '');
                coverUrl = `${baseUrl}/${item.cover}`;
            } else if (item.cover.startsWith('http')) {
                // Full URL provided
                coverUrl = item.cover;
            } else {
                // Local asset
                coverUrl = `assets/${item.cover}`;
            }
        }
        
        // Determine badge based on type or other criteria
        let badge = '';
        if (type === 'general' && Math.random() > 0.7) {
            badge = '<div class="book-badge">Bestseller</div>';
        } else if (type === 'setbook' && Math.random() > 0.8) {
            badge = '<div class="book-badge">New</div>';
        }
        
        // Get grade/class info
        const grade = item.grade || item.class || 'Standard 7';
        const subject = item.subject || 'Mathematics';
        
        card.innerHTML = `
            <div class="book-header">
                <img src="${coverUrl}" alt="${item.title}" class="book-image">
                ${badge}
            </div>
            <div class="book-info">
                <h3>${item.title}</h3>
                <div class="book-meta">
                    <div class="book-meta-left">
                        <i class="fas fa-book"></i>
                        <span>${grade}</span>
                    </div>
                    <div class="book-meta-right">
                        <i class="fas fa-file-pdf"></i>
                        <span>PDF</span>
                    </div>
                </div>
                <p class="book-desc">${item.description}</p>
                <div class="book-actions">
                    <button class="btn-download">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    // Download button logic
    grid.querySelectorAll('.btn-download').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('.book-card');
            const resourceId = card ? card.getAttribute('data-id') : null;
            if (isNullOrEmpty(resourceId)) {
                alert('Resource ID not found.');
                console.error('Attempted to download with null/undefined resourceId:', resourceId);
                return;
            }
            currentDownloadResourceId = resourceId;
            openModal(document.getElementById('download-modal'));
            document.getElementById('download-form').style.display = '';
            document.getElementById('download-modal-message').textContent = '';
            // Hide and disable the PesaPal button by default
            const pesapalBtn = document.getElementById('download-pesapal-btn');
            pesapalBtn.style.display = 'none';
            pesapalBtn.disabled = true;
        });
    });
    // Download modal logic
    const downloadModal = document.getElementById('download-modal');
    const downloadForm = document.getElementById('download-form');
    const downloadPesapalBtn = document.getElementById('download-pesapal-btn');
    if (downloadForm && downloadPesapalBtn) {
        downloadForm.onsubmit = function(e) {
            e.preventDefault();
            const name = document.getElementById('download-name').value;
            const email = document.getElementById('download-email').value;
            const phone = document.getElementById('download-phone').value;
            if (!name || !email || !phone) {
                document.getElementById('download-modal-message').textContent = 'Please fill in all fields.';
                return;
            }
            downloadFormData = { name, email, phone };
            document.getElementById('download-modal-message').textContent = 'Redirecting to PesaPal for payment...';
            // Show and enable the PesaPal button (for fallback, but we will auto-trigger payment)
            downloadPesapalBtn.style.display = '';
            downloadPesapalBtn.disabled = false;
            downloadForm.style.display = 'none';
            // Automatically trigger payment
            if (!isNullOrEmpty(currentDownloadResourceId) && downloadFormData) {
                fetch(`${API_BASE}/pay`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        resource_id: currentDownloadResourceId,
                        email: downloadFormData.email,
                        amount: 100,
                        name: downloadFormData.name,
                        phone: downloadFormData.phone
                    })
                })
                .then(res => res.json())
                .then(data => {
                    console.log('Payment API response:', data); // Debug logging
                    
                    if (data.success && data.message && data.message.includes('Test payment')) {
                        // Test payment successful
                        document.getElementById('download-modal-message').innerHTML =
                            '<div style="color: green;">✅ ' + data.message + '</div>' +
                            '<a href="download-success.html?resource_id=' +
                            encodeURIComponent(currentDownloadResourceId) + '&email=' +
                            encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                            encodeURIComponent(data.orderTrackingId) + '" target="_blank">Click here to download your resource</a>';
                    } else if (data.payment_url) {
                        // PesaPal payment - redirect to payment page
                        console.log('Opening PesaPal payment URL:', data.payment_url); // Debug logging
                        window.open(data.payment_url, '_blank');
                        document.getElementById('download-modal-message').innerHTML =
                            'After completing payment, <a href="download-success.html?resource_id=' +
                            encodeURIComponent(currentDownloadResourceId) + '&email=' +
                            encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                            encodeURIComponent(data.orderTrackingId) + '" target="_blank">click here to download your resource</a>.';
                    } else {
                        console.error('Unexpected payment response:', data); // Debug logging
                        document.getElementById('download-modal-message').textContent = data.error || 'Failed to initiate payment.';
                    }
                })
                .catch((error) => {
                    console.error('Payment API error:', error);
                    document.getElementById('download-modal-message').textContent = 'Failed to connect to payment API.';
                });
            }
        };
        // Keep the fallback click handler for the PesaPal button (in case auto-trigger fails)
        downloadPesapalBtn.onclick = function() {
            if (isNullOrEmpty(currentDownloadResourceId) || !downloadFormData) {
                alert('Missing resource or form data.');
                console.error('Download attempted with:', currentDownloadResourceId, downloadFormData);
                return;
            }
            fetch(`${API_BASE}/pay`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resource_id: currentDownloadResourceId,
                    email: downloadFormData.email,
                    amount: 100,
                    name: downloadFormData.name,
                    phone: downloadFormData.phone
                })
            })
            .then(res => res.json())
            .then(data => {
                console.log('Payment API response (fallback):', data); // Debug logging
                
                if (data.success && data.message && data.message.includes('Test payment')) {
                    // Test payment successful
                    document.getElementById('download-modal-message').innerHTML =
                        '<div style="color: green;">✅ ' + data.message + '</div>' +
                        '<a href="download-success.html?resource_id=' +
                        encodeURIComponent(currentDownloadResourceId) + '&email=' +
                        encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                        encodeURIComponent(data.orderTrackingId) + '" target="_blank">Click here to download your resource</a>';
                } else if (data.payment_url) {
                    // PesaPal payment - redirect to payment page
                    console.log('Opening PesaPal payment URL (fallback):', data.payment_url); // Debug logging
                    window.open(data.payment_url, '_blank');
                    document.getElementById('download-modal-message').innerHTML =
                        'After completing payment, <a href="download-success.html?resource_id=' +
                        encodeURIComponent(currentDownloadResourceId) + '&email=' +
                        encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                        encodeURIComponent(data.orderTrackingId) + '" target="_blank">click here to download your resource</a>.';
                } else {
                    console.error('Unexpected payment response (fallback):', data); // Debug logging
                    document.getElementById('download-modal-message').textContent = data.error || 'Failed to initiate payment.';
                }
            })
            .catch((error) => {
                console.error('Payment API error:', error);
                document.getElementById('download-modal-message').textContent = 'Failed to connect to payment API.';
            });
        };
    }
}

// Modal open/close helpers
function openModal(modal) {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}
function closeModal(modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
    if (modal.id === 'download-modal') {
        resetDownloadState();
    }
}
// Add close logic for modal close buttons
if (typeof document !== 'undefined') {
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) closeModal(modal);
        });
    });
}

// Enhanced authentication functions
function checkUserAuth() {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (user) {
        currentUser = user;
        console.log('User authenticated:', user.username);
    }
    updateAuthUI();
}

// Toggle mobile menu
document.querySelector('.hamburger-menu').addEventListener('click', function() {
    this.classList.toggle('open');
    document.querySelector('.mobile-menu-overlay').classList.toggle('active');
});

// // Close mobile menu
// document.querySelector('.mobile-menu-close').addEventListener('click', function() {
//     document.querySelector('.mobile-menu-overlay').classList.remove('active');
//     document.querySelector('.hamburger-menu').classList.remove('open');
// });

// // Close mobile menu when clicking on a link
// document.querySelectorAll('.mobile-nav a').forEach(link => {
//     link.addEventListener('click', function() {
//         document.querySelector('.mobile-menu-overlay').classList.remove('active');
//         document.querySelector('.hamburger-menu').classList.remove('open');
//     });
// });

function updateAuthUI() {
    console.log('🔄 Updating authentication UI...');
    console.log('Current user:', currentUser);
    
    const userActions = document.querySelector('.user-actions');
    if (!userActions) {
        console.error('❌ user-actions div not found');
        return;
    }
    
    console.log('✅ Found user-actions div');

    if (currentUser) {
        // User is logged in - show user info and logout
        console.log('👤 User is logged in, showing welcome message');
        userActions.innerHTML = `
            <span class="user-welcome">Welcome, ${currentUser.username}!</span>
            <a href="#" class="sign-out-link">Sign Out</a>
        `;
        
        // Add logout functionality
        const signOutLink = userActions.querySelector('.sign-out-link');
        if (signOutLink) {
            signOutLink.addEventListener('click', function(e) {
                e.preventDefault();
                signOut();
            });
        }
    } else {
        // User is not logged in - show sign in/register buttons
        console.log('🔐 User is not logged in, showing sign in/register buttons');
        userActions.innerHTML = `
            <a href="#" class="sign-in-link">Sign In</a>
            <a href="#" class="register-link">Register</a>
        `;
        
        // Add event listeners for sign in and register
        const signInLink = userActions.querySelector('.sign-in-link');
        const registerLink = userActions.querySelector('.register-link');
        
        if (signInLink) {
            signInLink.addEventListener('click', function(e) {
                e.preventDefault();
                openModal(document.getElementById('signin-modal'));
            });
        }
        
        if (registerLink) {
            registerLink.addEventListener('click', function(e) {
                e.preventDefault();
                openModal(document.getElementById('register-modal'));
            });
        }
    }
    
    console.log('✅ Authentication UI updated successfully');
}

function signOut() {
    localStorage.removeItem('currentUser');
    currentUser = null;
    updateAuthUI();
    console.log('User signed out');
}

// Enhanced modal functionality
function setupModalEventListeners() {
    // Sign In form submission
    const signinForm = document.getElementById('signin-form');
    if (signinForm) {
        signinForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('signin-username').value;
            const password = document.getElementById('signin-password').value;
            
            if (!username || !password) {
                alert('Please fill in all fields');
                return;
            }
            
            // Show loading state
            const submitBtn = signinForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Signing In...';
            submitBtn.disabled = true;
            
            console.log('🔐 Attempting login with:', { username, password: '***' });
            
            fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            })
            .then(res => {
                console.log('📡 Login response status:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('📡 Login response data:', data);
                
                if (data.success) {
                    currentUser = data.user;
                    localStorage.setItem('currentUser', JSON.stringify(data.user));
                    updateAuthUI();
                    closeModal(document.getElementById('signin-modal'));
                    signinForm.reset();
                    alert('Successfully signed in!');
                } else {
                    console.error('❌ Login failed:', data.error);
                    alert(data.error || 'Sign in failed');
                }
            })
            .catch(error => {
                console.error('❌ Sign in error:', error);
                alert('Sign in failed. Please try again.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // Register form submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('register-username').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            
            if (!username || !email || !password) {
                alert('Please fill in all fields');
                return;
            }
            
            // Show loading state
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Registering...';
            submitBtn.disabled = true;
            
            console.log('📝 Attempting registration with:', { username, email, password: '***' });
            
            fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            })
            .then(res => {
                console.log('📡 Registration response status:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('📡 Registration response data:', data);
                
                if (data.success) {
                    alert('Registration successful! Please sign in.');
                    closeModal(document.getElementById('register-modal'));
                    registerForm.reset();
                    // Switch to sign in modal
                    openModal(document.getElementById('signin-modal'));
                } else {
                    console.error('❌ Registration failed:', data.error);
                    alert(data.error || 'Registration failed');
                }
            })
            .catch(error => {
                console.error('❌ Registration error:', error);
                alert('Registration failed. Please try again.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // Modal switching functionality
    const showRegisterLink = document.querySelector('.show-register-link');
    const showSigninLink = document.querySelector('.show-signin-link');
    
    if (showRegisterLink) {
        showRegisterLink.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal(document.getElementById('signin-modal'));
            openModal(document.getElementById('register-modal'));
        });
    }
    
    if (showSigninLink) {
        showSigninLink.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal(document.getElementById('register-modal'));
            openModal(document.getElementById('signin-modal'));
        });
    }
}

// Enhanced main initialization
function mainAppInit() {
    console.log('🚀 Initializing main application...');
    
    // Check for existing user session FIRST
    checkUserAuth();
    console.log('✅ Authentication check completed');
    
    // Initialize revision slider
    initRevisionSlider();
    
    // Setup modal event listeners
    setupModalEventListeners();
    
    // Fetch and render resources
    fetchAndRenderResources();
    setInterval(fetchAndRenderResources, 10000); // Auto-refresh every 10 seconds
    
    // Class/Grade selector functionality
    const classSelect = document.getElementById('class-select');
    const subjectSelect = document.getElementById('subject-select');
    
    // Enable subject select when a class is chosen
    if (classSelect && subjectSelect) {
        classSelect.addEventListener('change', function() {
            if (this.value) {
                subjectSelect.disabled = false;
                // Populate subjects based on class/grade
                let subjects = [];
                
                if (this.value.includes('std')) {
                    // KCPE (Primary School) subjects
                    subjects = [
                        { value: 'English', label: 'English' },
                        { value: 'Kiswahili', label: 'Kiswahili' },
                        { value: 'Mathematics', label: 'Mathematics' },
                        { value: 'Science', label: 'Science' },
                        { value: 'Social Studies', label: 'Social Studies' },
                        { value: 'Religious Education', label: 'Religious Education' }
                    ];
                } else if (this.value.includes('form')) {
                    // KCSE (Secondary School) subjects
                    subjects = [
                        { value: 'English', label: 'English' },
                        { value: 'Kiswahili', label: 'Kiswahili' },
                        { value: 'Mathematics', label: 'Mathematics' },
                        { value: 'Biology', label: 'Biology' },
                        { value: 'Chemistry', label: 'Chemistry' },
                        { value: 'Physics', label: 'Physics' },
                        { value: 'History', label: 'History' },
                        { value: 'Geography', label: 'Geography' },
                        { value: 'Religious Education', label: 'Religious Education' },
                        { value: 'Business Studies', label: 'Business Studies' },
                        { value: 'Agriculture', label: 'Agriculture' },
                        { value: 'Home Science', label: 'Home Science' },
                        { value: 'Computer Studies', label: 'Computer Studies' }
                    ];
                } else if (this.value.includes('pp')) {
                    // CBC PP1 & PP2 subjects
                    subjects = [
                        { value: 'Language Activities', label: 'Language Activities' },
                        { value: 'Mathematical Activities', label: 'Mathematical Activities' },
                        { value: 'Environmental Activities', label: 'Environmental Activities' },
                        { value: 'Creative Activities', label: 'Creative Activities' },
                        { value: 'Religious Activities', label: 'Religious Activities' }
                    ];
                } else if (this.value.includes('grade')) {
                    // CBC Grades 1-12 subjects
                    subjects = [
                        { value: 'English', label: 'English' },
                        { value: 'Kiswahili', label: 'Kiswahili' },
                        { value: 'Kenya Sign Language', label: 'Kenya Sign Language' },
                        { value: 'Mathematics', label: 'Mathematics' },
                        { value: 'Religious Education', label: 'Religious Education' },
                        { value: 'Environmental Activities', label: 'Environmental Activities' },
                        { value: 'Creative Activities', label: 'Creative Activities' },
                        { value: 'Science and Technology', label: 'Science and Technology' },
                        { value: 'Agriculture and Nutrition', label: 'Agriculture and Nutrition' },
                        { value: 'Social Studies', label: 'Social Studies' },
                        { value: 'Arts and Craft', label: 'Arts and Craft' },
                        { value: 'Music', label: 'Music' },
                        { value: 'Physical and Health Education', label: 'Physical and Health Education' },
                        { value: 'Integrated Science', label: 'Integrated Science' },
                        { value: 'Pre-Technical and Pre-Career Education', label: 'Pre-Technical and Pre-Career Education' },
                        { value: 'Business Studies', label: 'Business Studies' },
                        { value: 'Health Education', label: 'Health Education' },
                        { value: 'Life Skills Education', label: 'Life Skills Education' },
                        { value: 'Computer Science', label: 'Computer Science' },
                        { value: 'Home Science', label: 'Home Science' },
                        { value: 'Community Service Learning', label: 'Community Service Learning' },
                        { value: 'Physics', label: 'Physics' },
                        { value: 'Chemistry', label: 'Chemistry' },
                        { value: 'Biology', label: 'Biology' },
                        { value: 'Fine Art', label: 'Fine Art' },
                        { value: 'Performing Arts', label: 'Performing Arts' },
                        { value: 'Sports Science', label: 'Sports Science' },
                        { value: 'History', label: 'History' },
                        { value: 'Geography', label: 'Geography' },
                        { value: 'Literature in English', label: 'Literature in English' }
                    ];
                }
                
                // Clear and populate subject select
                subjectSelect.innerHTML = '<option value="">Select Subject</option>';
                subjects.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject.value;
                    option.textContent = subject.label;
                    subjectSelect.appendChild(option);
                });
            } else {
                subjectSelect.disabled = true;
                subjectSelect.innerHTML = '<option value="">Select Subject</option>';
            }
        });
    }
    
    // Find Resources button functionality
    const findResourcesBtn = document.getElementById('find-resources');
    if (findResourcesBtn) {
        findResourcesBtn.addEventListener('click', function() {
            const selectedClass = classSelect ? classSelect.value : '';
            const selectedSubject = subjectSelect ? subjectSelect.value : '';
            
            if (selectedClass && selectedSubject) {
                window.location.href = `resources.html?class=${encodeURIComponent(selectedClass)}&subject=${encodeURIComponent(selectedSubject)}`;
            } else {
                alert('Please select both class and subject');
            }
        });
    }
    
    console.log('✅ Main application initialized successfully');
}

// Smooth scrolling for anchor links (About, Contact, etc.)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href && href.startsWith('#') && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});
// Contact form logic
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.onsubmit = function(e) {
        e.preventDefault();
        document.getElementById('contact-message-status').textContent = 'Thank you for contacting us! We will get back to you soon.';
        contactForm.reset();
    };
}

// Newsletter subscription logic
const newsletterBtn = document.querySelector('.newsletter-btn');
const newsletterInput = document.querySelector('.newsletter-input');

if (newsletterBtn && newsletterInput) {
    newsletterBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const email = newsletterInput.value.trim();
        
        if (!email) {
            alert('Please enter your email address.');
            return;
        }
        
        if (!email.includes('@')) {
            alert('Please enter a valid email address.');
            return;
        }
        
        // Show success message
        newsletterBtn.textContent = 'Subscribed!';
        newsletterBtn.style.backgroundColor = '#2e8b57';
        newsletterInput.value = '';
        
        setTimeout(() => {
            newsletterBtn.textContent = 'Subscribe';
            newsletterBtn.style.backgroundColor = '';
        }, 2000);
    });
}

// Main initialization - consolidate all DOMContentLoaded listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing user dashboard...');
    
    // First, set up API base URL
    fetchApiBaseUrl().then(() => {
        // Then initialize the main app
        mainAppInit();
        
        // Set up modal links for Sign In and Register
        document.querySelectorAll('.user-actions a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                if (this.textContent.includes('Sign In') || this.classList.contains('sign-in-link')) {
                    console.log('Sign In clicked');
                    openModal(document.getElementById('signin-modal'));
                } else if (this.textContent.includes('Register')) {
                    console.log('Register clicked');
                    openModal(document.getElementById('register-modal'));
                }
            });
        });
        
        // Set up modal switching links
        const showRegisterLink = document.getElementById('show-register');
        const showSigninLink = document.getElementById('show-signin');
        
        if (showRegisterLink) {
            showRegisterLink.addEventListener('click', function(e) {
                e.preventDefault();
                closeModal(document.getElementById('signin-modal'));
                openModal(document.getElementById('register-modal'));
            });
        }
        
        if (showSigninLink) {
            showSigninLink.addEventListener('click', function(e) {
                e.preventDefault();
                closeModal(document.getElementById('register-modal'));
                openModal(document.getElementById('signin-modal'));
            });
        }
        
        // Set up modal close buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', function() {
                const modalId = this.getAttribute('data-modal');
                const modal = document.getElementById(modalId);
                if (modal) closeModal(modal);
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target.classList.contains('modal')) {
                closeModal(event.target);
            }
        });
        
        console.log('✅ All event listeners set up successfully');
    });
});
