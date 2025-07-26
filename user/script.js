// Revision Papers Data
const revisionPapers = [
    { image: "assets/exam paper2.jpg" },
    { image: "assets/WhatsApp Image 2025-07-21 at 17.39.48_efa085dc.jpg" }
];

// Add this helper at the top for robust null/undefined checks
function isNullOrEmpty(val) {
    return val === null || val === undefined || val === '';
}

// Add these at the top of the file, outside any function:
let currentDownloadResourceId = null;
let downloadFormData = null;
let API_BASE = '';

function fetchApiBaseUrl() {
    return fetch('/api/config')
        .then(res => res.json())
        .then(cfg => {
            API_BASE = cfg.API_BASE_URL;
            console.log('API Base URL loaded:', API_BASE);
        })
        .catch(error => {
            console.error('Failed to load API config:', error);
            // Fallback to localhost for development
            API_BASE = 'http://localhost:5000/api';
        });
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
    
    fetch(`${API_BASE}/resources`)
        .then(res => res.json())
        .then(data => {
            renderGeneralResources('.books-section', data.books, 'general');
            renderGeneralResources('#papers', data.papers, 'paper');
            renderGeneralResources('#setbooks', data.setbooks, 'setbook');
        })
        .catch((error) => {
            console.error('Failed to fetch resources:', error);
            renderGeneralResources('.books-section', [], 'general');
            renderGeneralResources('#papers', [], 'paper');
            renderGeneralResources('#setbooks', [], 'setbook');
        });
}

// Initialize the revision papers slider
function initRevisionSlider() {
    const sliderContainer = document.querySelector('.slider-container');
    const sliderNav = document.querySelector('.slider-nav');
    
    // Clear existing content
    sliderContainer.innerHTML = '';
    sliderNav.innerHTML = '';
    
    // Add slides to the slider
    revisionPapers.forEach((paper, index) => {
        // Create slider item
        const sliderItem = document.createElement('div');
        sliderItem.className = 'slider-item';
        sliderItem.innerHTML = `
            <img src="${paper.image}" alt="Slider Image ${index + 1}" class="slider-image">
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
        let coverUrl = item.cover && item.cover !== 'null' ? item.cover : 'assets/placeholder.jpg';
        if (item.cover && item.cover.startsWith('static/covers/')) {
            // Use the base URL without /api for static files
            const baseUrl = API_BASE.replace('/api', '');
            coverUrl = `${baseUrl}/${item.cover}`;
        }
        if (!item.cover || item.cover === 'null') {
            console.warn('Resource with missing cover:', item);
        }
        card.innerHTML = `
            <div class="book-cover" style="background-image: url('${coverUrl}')"></div>
            <div class="book-info">
                <div class="book-category">${item.category}</div>
                <h3 class="book-title">${item.title}</h3>
                <p class="book-description">${item.description}</p>
                <div class="book-meta">
                    <div class="book-price">Ksh ${item.price}</div>
                    <button class="btn btn-outline download-btn">Download</button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    // Download button logic
    grid.querySelectorAll('.download-btn').forEach(button => {
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
                    if (data.payment_url) {
                        // Redirect to payment page in a new tab
                        window.open(data.payment_url, '_blank');
                        document.getElementById('download-modal-message').innerHTML =
                            'After completing payment, <a href="download-success.html?resource_id=' +
                            encodeURIComponent(currentDownloadResourceId) + '&email=' +
                            encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                            encodeURIComponent(data.orderTrackingId) + '" target="_blank">click here to download your resource</a>.';
                    } else {
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
                if (data.payment_url) {
                    window.open(data.payment_url, '_blank');
                    document.getElementById('download-modal-message').innerHTML =
                        'After completing payment, <a href="download-success.html?resource_id=' +
                        encodeURIComponent(currentDownloadResourceId) + '&email=' +
                        encodeURIComponent(downloadFormData.email) + '&orderTrackingId=' +
                        encodeURIComponent(data.orderTrackingId) + '" target="_blank">click here to download your resource</a>.';
                } else {
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

// Initialize the slider when the page loads
function mainAppInit() {
    const signinModal = document.getElementById('signin-modal');
    const registerModal = document.getElementById('register-modal');
    initRevisionSlider();
    fetchAndRenderResources();
    setInterval(fetchAndRenderResources, 10000); // Auto-refresh every 10 seconds
    
    // Class/Grade selector functionality
    const classSelect = document.getElementById('class-select');
    const subjectSelect = document.getElementById('subject-select');
    
    // Enable subject select when a class is chosen
    classSelect.addEventListener('change', function() {
        if (this.value) {
            subjectSelect.disabled = false;
            // In a real implementation, you would populate subjects based on class
            // For this example, we'll just show a static list
            subjectSelect.innerHTML = `
                <option value="">Select Subject</option>
                <option value="math">Mathematics</option>
                <option value="english">English</option>
                <option value="kiswahili">Kiswahili</option>
                <option value="science">Science</option>
                <option value="social">Social Studies</option>
                <option value="cre">CRE</option>
            `;
        } else {
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">First select a class/grade</option>';
        }
    });
    
    // Find resources button
    const findResourcesBtn = document.getElementById('find-resources');
    findResourcesBtn.addEventListener('click', function() {
        const selectedClass = classSelect.value;
        const selectedSubject = subjectSelect.value;
        
        if (isNullOrEmpty(selectedClass)) {
            alert('Please select a class/grade');
            return;
        }
        
        if (isNullOrEmpty(selectedSubject)) {
            alert('Please select a subject');
            return;
        }
        
        // Redirect to subject.html with query params
        window.location.href = `subject.html?class=${encodeURIComponent(selectedClass)}&subject=${encodeURIComponent(selectedSubject)}`;
    });

    // Prevent form submission (demo only)
    document.getElementById('signin-form').onsubmit = function(e) {
        e.preventDefault();
        const form = e.target;
        const username = form.querySelector('input[type="text"]').value;
        const password = form.querySelector('input[type="password"]').value;
        fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Sign in successful!');
                closeModal(signinModal);
            } else {
                alert(data.error || 'Sign in failed');
            }
        })
        .catch((error) => {
            console.error('Login API error:', error);
            alert('Failed to connect to backend API.');
        });
    };
    document.getElementById('register-form').onsubmit = function(e) {
            e.preventDefault();
        const form = e.target;
        const username = form.querySelector('input[type="text"]').value;
        const email = form.querySelector('input[type="email"]').value;
        const password = form.querySelector('input[type="password"]').value;
        fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Registration successful! You can now sign in.');
                closeModal(registerModal);
            } else {
                alert(data.error || 'Registration failed');
            }
        })
        .catch((error) => {
            console.error('Register API error:', error);
            alert('Failed to connect to backend API.');
        });
    };
    
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
    // Ensure Sign In and Register links open their modals (fix)
    document.querySelectorAll('.user-actions a').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.textContent.includes('Sign In')) {
                e.preventDefault();
                console.log('Sign In clicked');
                openModal(signinModal);
            }
            if (this.textContent.includes('Register')) {
                e.preventDefault();
                console.log('Register clicked');
                openModal(registerModal);
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
}

document.addEventListener('DOMContentLoaded', function() {
    fetchApiBaseUrl().then(mainAppInit);
});