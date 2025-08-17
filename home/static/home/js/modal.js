// 팀원 카드 클릭 시 모달에 iframe src 설정
document.querySelectorAll('.card a').forEach(link => {
  link.addEventListener('click', event => {
    event.preventDefault(); // 기본 링크 이동 막기

    // 예제에서는 링크의 href를 iframe에 적용
    const url = link.getAttribute('href');
    document.getElementById('modalIframe').src = url;
    
    document.getElementById('profileModal').style.display = 'block';
  });
});

// 모달 닫기 함수
function closeModal() {
  document.getElementById('profileModal').style.display = 'none';
  document.getElementById('modalIframe').src = "";
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
  const modal = document.getElementById('profileModal');
  if (event.target === modal) {
    closeModal();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('profileModal');
  const iframe = document.getElementById('modalIframe');
  const closeBtn = document.querySelector('.close-button');
  let escHandler = null;

  function openModal(url) {
    iframe.src = url;
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    escHandler = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', escHandler);
  }

  function closeModal() {
    modal.style.display = 'none';
    iframe.src = '';
    document.body.style.overflow = '';

    if (escHandler) {
      window.removeEventListener('keydown', escHandler);
      escHandler = null;
    }
  }

  // 외부에서도 호출 가능(템플릿의 onclick="closeModal()")
  window.closeModal = closeModal;

  // 카드 클릭 시 모달 오픈
  document.querySelectorAll('.card a').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(link.getAttribute('href'));
    });
  });

  // 오버레이 영역 클릭 시 닫기
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
});