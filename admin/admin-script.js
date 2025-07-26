// --- DASHBOARD STATS & SIDEBAR LOGIC ---
let API_BASE = '';

function fetchApiBaseUrl() {
    return fetch('/api/config')
        .then(res => res.json())
        .then(cfg => {
            API_BASE = cfg.API_BASE_URL;
            console.log('Admin API Base URL loaded:', API_BASE);
        })
        .catch(error => {
            console.error('Failed to load API config:', error);
            // Fallback to deployed backend for production
            API_BASE = 'https://books-management-system-bcr5.onrender.com/api';
        });
}

function fetchAndUpdateStats() {
    if (!API_BASE) {
        console.warn('API_BASE not loaded yet, skipping stats fetch');
        return;
    }
    
    fetch(`${API_BASE}/resources`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('stat-books').textContent = data.books.length;
            document.getElementById('stat-papers').textContent = data.papers.length;
            document.getElementById('stat-setbooks').textContent = data.setbooks.length;
        })
        .catch(error => {
            console.error('Failed to fetch stats:', error);
        });
        
    fetch(`${API_BASE}/users`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('stat-users').textContent = data.count;
        })
        .catch(error => {
            console.error('Failed to fetch user count:', error);
        });
}

function fetchAndRenderList(type, containerId) {
    if (!API_BASE) {
        console.warn('API_BASE not loaded yet, skipping list fetch');
        return;
    }
    
    fetch(`${API_BASE}/resources`)
        .then(res => res.json())
        .then(data => {
            const list = data[type];
            const container = document.getElementById(containerId);
            if (!container) return;
            if (!list.length) {
                container.innerHTML = '<div style="color:#888;">No resources found.</div>';
                return;
            }
            container.innerHTML = list.map(item => `
                <div class="admin-list-item" style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                    ${item.cover ? `<img src="${API_BASE.replace('/api', '')}/${item.cover}" alt="Cover" style="width:60px;height:80px;object-fit:cover;border-radius:6px;">` : ''}
                    <div style="flex:1;">
                        <strong>${item.title}</strong> (${item.class_grade} - ${item.subject})<br>
                        <span>${item.description}</span>
                    </div>
                    <button class="btn btn-outline delete-btn" data-id="${item.id}" style="color:#B22222;border-color:#B22222;">Delete</button>
                </div>
            `).join('');
            // Attach delete handlers
            container.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const id = this.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this resource?')) {
                        fetch(`${API_BASE}/resource/${id}`, {
                            method: 'DELETE'
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                fetchAndUpdateStats();
                                fetchAndRenderList(type, containerId);
                            } else {
                                alert(data.error || 'Delete failed.');
                            }
                        })
                        .catch((error) => {
                            console.error('Delete API error:', error);
                            alert('Failed to connect to backend API.');
                        });
                    }
                });
            });
        })
        .catch((error) => {
            console.error('Failed to fetch resources:', error);
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = '<div style="color:#888;">Failed to load resources.</div>';
            }
        });
}

function mainAdminInit() {
    // Subjects by class/grade
    const subjects = {
        // KCPE
        std1: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std2: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std3: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std4: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std5: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std6: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std7: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        std8: ["English", "Kiswahili", "Mathematics", "Science", "Social Studies", "Religious Education"],
        
        // KCSE
        form1: ["English", "Kiswahili", "Mathematics", "Biology", "Chemistry", "Physics", "History", "Geography", "Religious Education", "Business Studies", "Agriculture", "Home Science", "Computer Studies"],
        form2: ["English", "Kiswahili", "Mathematics", "Biology", "Chemistry", "Physics", "History", "Geography", "Religious Education", "Business Studies", "Agriculture", "Home Science", "Computer Studies"],
        form3: ["English", "Kiswahili", "Mathematics", "Biology", "Chemistry", "Physics", "History", "Geography", "Religious Education", "Business Studies", "Agriculture", "Home Science", "Computer Studies"],
        form4: ["English", "Kiswahili", "Mathematics", "Biology", "Chemistry", "Physics", "History", "Geography", "Religious Education", "Business Studies", "Agriculture", "Home Science", "Computer Studies"],
        
        // CBC
        pp1: ["Language Activities", "Mathematical Activities", "Environmental Activities", "Creative Activities", "Religious Activities"],
        pp2: ["Language Activities", "Mathematical Activities", "Environmental Activities", "Creative Activities", "Religious Activities"],
        grade1: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Environmental Activities", "Creative Activities"],
        grade2: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Environmental Activities", "Creative Activities"],
        grade3: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Environmental Activities", "Creative Activities"],
        grade4: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Science and Technology", "Agriculture and Nutrition", "Social Studies", "Arts and Craft", "Music", "Physical and Health Education"],
        grade5: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Science and Technology", "Agriculture and Nutrition", "Social Studies", "Arts and Craft", "Music", "Physical and Health Education"],
        grade6: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Science and Technology", "Agriculture and Nutrition", "Social Studies", "Arts and Craft", "Music", "Physical and Health Education"],
        grade7: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Integrated Science", "Pre-Technical and Pre-Career Education", "Business Studies", "Social Studies", "Health Education", "Life Skills Education", "Computer Science", "Home Science", "Community Service Learning"],
        grade8: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Integrated Science", "Pre-Technical and Pre-Career Education", "Business Studies", "Social Studies", "Health Education", "Life Skills Education", "Computer Science", "Home Science", "Community Service Learning"],
        grade9: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Integrated Science", "Pre-Technical and Pre-Career Education", "Business Studies", "Social Studies", "Health Education", "Life Skills Education", "Computer Science", "Home Science", "Community Service Learning"],
        grade10: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Physics", "Chemistry", "Biology", "Business Studies", "Computer Science", "Home Science", "Agriculture", "Fine Art", "Performing Arts", "Sports Science", "History", "Geography", "Literature in English"],
        grade11: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Physics", "Chemistry", "Biology", "Business Studies", "Computer Science", "Home Science", "Agriculture", "Fine Art", "Performing Arts", "Sports Science", "History", "Geography", "Literature in English"],
        grade12: ["English", "Kiswahili", "Kenya Sign Language", "Mathematics", "Religious Education", "Physics", "Chemistry", "Biology", "Business Studies", "Computer Science", "Home Science", "Agriculture", "Fine Art", "Performing Arts", "Sports Science", "History", "Geography", "Literature in English"]
    };
    
    // DOM Elements
    const classGradeSelect = document.getElementById('class-grade');
    const subjectSelect = document.getElementById('subject');
    const uploadForm = document.getElementById('upload-form');
    const fileUploads = document.querySelectorAll('.file-upload');
    
    if (classGradeSelect && subjectSelect && uploadForm) {
    // Handle class/grade selection
    classGradeSelect.addEventListener('change', function() {
        const selectedClass = classGradeSelect.value;
        
        if (selectedClass) {
            subjectSelect.disabled = false;
            subjectSelect.innerHTML = '<option value="">Select Subject</option>';
            
            // Populate subjects
            subjects[selectedClass].forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.toLowerCase().replace(/\s+/g, '-');
                option.textContent = subject;
                subjectSelect.appendChild(option);
            });
        } else {
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Select Class/Grade First</option>';
        }
    });
    
    // Handle file upload interactions
    fileUploads.forEach(upload => {
        const input = upload.querySelector('input[type="file"]');
        
        upload.addEventListener('click', function() {
            input.click();
        });
        
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                upload.querySelector('p').textContent = fileName;
                upload.style.borderColor = 'var(--savanna-green)';
            }
        });
    });
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const resourceType = document.getElementById('resource-type').value;
        const classGrade = classGradeSelect.value;
        const subject = subjectSelect.value;
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
            const coverInput = uploadForm.querySelector('input[type="file"][accept^="image"]');
            const coverFile = coverInput && coverInput.files[0];
        
        // Simple validation
        if (!classGrade || !subject || !title) {
            alert('Please fill in all required fields');
            return;
        }
        
            // Prepare form data
            const formData = new FormData();
            formData.append('resourceType', resourceType);
            formData.append('classGrade', classGrade);
            formData.append('subject', subject);
            formData.append('title', title);
            formData.append('description', description);
            if (coverFile) {
                formData.append('cover', coverFile);
            }
            
            // Send to backend API
            fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Resource uploaded successfully!');
        uploadForm.reset();
        subjectSelect.disabled = true;
        subjectSelect.innerHTML = '<option value="">Select Class/Grade First</option>';
        document.querySelectorAll('.file-upload p').forEach(p => {
            p.textContent = 'Click to upload';
                    });
                    document.querySelectorAll('.file-upload').forEach(upload => {
                        upload.style.borderColor = 'var(--light-gray)';
                    });
                    // Refresh dashboard stats and lists
                    fetchAndUpdateStats();
                    fetchAndRenderList('books', 'books-list');
                    fetchAndRenderList('papers', 'papers-list');
                    fetchAndRenderList('setbooks', 'setbooks-list');
                } else {
                    alert('Upload failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch((error) => {
                console.error('Upload API error:', error);
                alert('Failed to connect to backend API.');
            });
        });
    }

    // Admin login modal logic
    const adminLoginModal = document.getElementById('admin-login-modal');
    const adminDashboard = document.getElementById('admin-dashboard');
    const adminLoginForm = document.getElementById('admin-login-form');
    if (adminLoginModal && adminLoginForm && adminDashboard) {
        adminDashboard.style.display = 'none';
        adminLoginModal.style.display = 'flex';
        adminLoginForm.onsubmit = function(e) {
            e.preventDefault();
            const username = adminLoginForm.querySelector('input[type="text"]').value;
            const password = adminLoginForm.querySelector('input[type="password"]').value;
            const errorDiv = document.getElementById('login-error');
            errorDiv.textContent = '';
            fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    adminLoginModal.style.display = 'none';
                    adminDashboard.style.display = '';
                } else {
                    errorDiv.textContent = data.error || 'Login failed';
                }
            })
            .catch((error) => {
                console.error('Login API error:', error);
                errorDiv.textContent = 'Failed to connect to backend API.';
            });
        };
    }

    // --- DASHBOARD STATS & SIDEBAR LOGIC ---
    fetchAndUpdateStats();
    fetchAndRenderList('books', 'books-list');
    fetchAndRenderList('papers', 'papers-list');
    fetchAndRenderList('setbooks', 'setbooks-list');

    // Sidebar navigation
    document.querySelectorAll('.admin-menu a[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.admin-menu a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            const section = this.getAttribute('data-section');
            document.querySelectorAll('.admin-main > div[id^="section-"]').forEach(div => {
                div.style.display = 'none';
            });
            document.getElementById('section-' + section).style.display = '';
            // Fetch lists if needed
            if (section === 'books') fetchAndRenderList('books', 'books-list');
            if (section === 'papers') fetchAndRenderList('papers', 'papers-list');
            if (section === 'setbooks') fetchAndRenderList('setbooks', 'setbooks-list');
            if (section === 'upload') {
                // Ensure upload form is visible and ready
                if (classGradeSelect && subjectSelect && uploadForm) {
                    subjectSelect.disabled = true;
                    subjectSelect.innerHTML = '<option value="">Select Class/Grade First</option>';
                    uploadForm.reset();
                    document.querySelectorAll('.file-upload p').forEach(p => {
                        p.textContent = 'Click to upload';
                    });
        document.querySelectorAll('.file-upload').forEach(upload => {
            upload.style.borderColor = 'var(--light-gray)';
                    });
                }
            }
        });
    });
    // Show dashboard by default
    document.getElementById('section-dashboard').style.display = '';

    // Logout logic
    const adminLogout = document.getElementById('admin-logout');
    if (adminLogout) {
        adminLogout.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('admin-dashboard').style.display = 'none';
            document.getElementById('admin-login-modal').style.display = 'flex';
        });
    }

    // Settings form logic (change password)
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.onsubmit = function(e) {
            e.preventDefault();
            const oldPassword = document.getElementById('old-password').value;
            const newPassword = document.getElementById('new-password').value;
            const msgDiv = document.getElementById('settings-message');
            msgDiv.textContent = '';
            fetch(`${API_BASE}/change_password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: 'admin',
                    old_password: oldPassword,
                    new_password: newPassword
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    msgDiv.textContent = 'Password updated successfully!';
                    msgDiv.style.color = 'green';
                    settingsForm.reset();
                } else {
                    msgDiv.textContent = data.error || 'Password update failed.';
                    msgDiv.style.color = '#B22222';
                }
            })
            .catch((error) => {
                console.error('Change password API error:', error);
                msgDiv.textContent = 'Failed to connect to backend API.';
                msgDiv.style.color = '#B22222';
            });
        };
    }

    // Cover image preview logic
    const coverInput = document.getElementById('cover-input');
    const coverPreview = document.getElementById('cover-preview');
    if (coverInput && coverPreview) {
        coverInput.addEventListener('change', function() {
            coverPreview.innerHTML = '';
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    coverPreview.innerHTML = `<img src="${e.target.result}" alt="Cover Preview" style="max-width:120px;max-height:160px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">`;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    // Subject dropdown population logic
    const classGradeSelect2 = document.getElementById('class-grade');
    const subjectSelect2 = document.getElementById('subject');
    if (classGradeSelect2 && subjectSelect2) {
        classGradeSelect2.addEventListener('change', function() {
            const selectedClass = classGradeSelect2.value;
            if (selectedClass && subjects[selectedClass]) {
                subjectSelect2.disabled = false;
                subjectSelect2.innerHTML = '<option value="">Select Subject</option>';
                subjects[selectedClass].forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject.toLowerCase().replace(/\s+/g, '-');
                    option.textContent = subject;
                    subjectSelect2.appendChild(option);
                });
            } else {
                subjectSelect2.disabled = true;
                subjectSelect2.innerHTML = '<option value="">Select Class/Grade First</option>';
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchApiBaseUrl().then(mainAdminInit);
});