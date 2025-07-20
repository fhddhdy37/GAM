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