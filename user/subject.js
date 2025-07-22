// Resources data (copy from script.js)
const resources = {
    books: [
        { class: 'form2', subject: 'mathematics', title: 'Mathematics Form 2 Textbook', description: 'Comprehensive textbook covering all Form 2 mathematics topics with practice questions and solutions.', price: 100, cover: 'assets/placeholder.jpg', category: 'Mathematics' },
        { class: 'form1', subject: 'english', title: 'English Grammar Guide', description: 'Master English grammar with this comprehensive guide for all secondary levels.', price: 100, cover: 'assets/placeholder.jpg', category: 'English' },
        { class: 'grade6', subject: 'science and technology', title: 'Integrated Science Grade 6', description: 'CBC-aligned science textbook with practical activities and experiments.', price: 100, cover: 'assets/placeholder.jpg', category: 'Science' },
        { class: 'std4', subject: 'kiswahili', title: 'Kiswahili kwa Shule za Msingi', description: 'Standard 4-8 Kiswahili textbook with grammar, comprehension, and composition.', price: 100, cover: 'assets/placeholder.jpg', category: 'Kiswahili' },
    ],
    papers: [
        { class: 'form4', subject: 'mathematics', title: 'Mathematics Paper 1', description: 'KCSE 2022 Mathematics Paper 1 with marking scheme.', price: 100, cover: 'assets/placeholder.jpg', category: 'KCSE 2022' },
        { class: 'std8', subject: 'science', title: 'Science Paper', description: 'KCPE 2021 Science paper with answers.', price: 100, cover: 'assets/placeholder.jpg', category: 'KCPE 2021' },
    ],
    setbooks: [
        { class: 'form3', subject: 'literature in english', title: 'The River and The Source', description: 'Setbook for KCSE English Paper 3 with study guide and analysis.', price: 100, cover: 'assets/placeholder.jpg', category: 'Literature' },
        { class: 'form3', subject: 'kiswahili', title: 'Chozi la Heri', description: 'Setbook for KCSE Kiswahili Paper 3 with annotations.', price: 100, cover: 'assets/placeholder.jpg', category: 'Kiswahili' },
    ]
};

// Helper to get query params
function getQueryParam(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
}

// Get class and subject from URL
const selectedClass = getQueryParam('class');
const selectedSubject = getQueryParam('subject');

// Find the book
const book = resources.books.find(b => b.class === selectedClass && b.subject.replace(/\s+/g, '-') === selectedSubject);

if (book) {
    document.getElementById('subject-cover').style.backgroundImage = `url('${book.cover}')`;
    document.getElementById('subject-title').textContent = book.title;
    document.getElementById('subject-category').textContent = book.category;
    document.getElementById('subject-description').textContent = book.description;
    document.getElementById('subject-price').textContent = `Ksh ${book.price}`;
} else {
    document.querySelector('.subject-details-container').innerHTML = '<div style="color:#B22222; font-size:1.2rem;">No book found for this selection.</div>';
}

// Payment modal logic
const modalOverlay = document.getElementById('modal-overlay');
const paymentModal = document.getElementById('payment-modal');
const downloadBtn = document.getElementById('subject-download');

function openModal(modal) {
    modalOverlay.style.display = 'flex';
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}
function closeModal(modal) {
    modalOverlay.style.display = 'none';
    modal.style.display = 'none';
    document.body.style.overflow = '';
}
function closeAllModals() {
    paymentModal.style.display = 'none';
    modalOverlay.style.display = 'none';
    document.body.style.overflow = '';
}

downloadBtn.onclick = function() {
    openModal(paymentModal);
};
document.getElementById('simulate-payment').onclick = function() {
    closeModal(paymentModal);
    setTimeout(() => alert('Payment successful! Download starting...'), 300);
};
document.querySelector('.close-modal').onclick = function() {
    closeModal(paymentModal);
};
modalOverlay.onclick = closeAllModals;
document.querySelector('.modal-content').onclick = e => e.stopPropagation(); 