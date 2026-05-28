// 모바일 네비게이션 토글
const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });

  // 외부 클릭 시 메뉴 닫기
  document.addEventListener('click', e => {
    if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
      navMenu.classList.remove('open');
    }
  });
}

// 파일 업로드 영역 클릭 처리
const uploadArea = document.getElementById('fileUploadArea');
if (uploadArea) {
  const fileInput = uploadArea.querySelector('input[type=file]');
  uploadArea.addEventListener('click', () => fileInput?.click());

  uploadArea.addEventListener('dragover', e => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--accent)';
  });
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '';
  });
  uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.style.borderColor = '';
    const file = e.dataTransfer.files[0];
    if (file && fileInput) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
}

// 메시지 자동 닫기 (5초)
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.opacity = '0';
    msg.style.transition = 'opacity 0.5s ease';
    setTimeout(() => msg.remove(), 500);
  }, 5000);
});
