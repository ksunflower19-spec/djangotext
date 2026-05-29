// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });

  document.addEventListener('click', e => {
    if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
      navMenu.classList.remove('open');
    }
  });
}

// File upload area click / drag-drop
const uploadArea = document.getElementById('fileUploadArea');
if (uploadArea) {
  const fileInput = uploadArea.querySelector('input[type=file]');
  uploadArea.addEventListener('click', () => fileInput?.click());

  uploadArea.addEventListener('dragover', e => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
  });
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
  });
  uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && fileInput) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
}

// Auto-dismiss flash messages after 5s
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.opacity = '0';
    msg.style.transition = 'opacity 0.4s ease';
    setTimeout(() => msg.remove(), 400);
  }, 5000);
});
