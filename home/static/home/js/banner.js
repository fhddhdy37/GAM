// main.js

let slideIndex = 0;

function showSlides() {
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  slides.forEach(slide => slide.style.display = 'none');
  dots.forEach(dot => dot.classList.remove('active'));
  slideIndex++;
  if (slideIndex > slides.length) { slideIndex = 1; }
  slides[slideIndex - 1].style.display = 'block';
  dots[slideIndex - 1].classList.add('active');
  setTimeout(showSlides, 5000);
}

function currentSlide(n) {
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  slides.forEach(slide => slide.style.display = 'none');
  dots.forEach(dot => dot.classList.remove('active'));
  slideIndex = n;
  slides[slideIndex - 1].style.display = 'block';
  dots[slideIndex - 1].classList.add('active');
}

function adjustImageSizes() {
  const container = document.querySelector('.slideshow-container');
  if (!container) return;

  const containerWidth = container.offsetWidth;
  const containerHeight = container.offsetHeight;
  const images = container.querySelectorAll('.slide img');
  images.forEach(img => {
    const naturalWidth = img.naturalWidth;
    const naturalHeight = img.naturalHeight;
    const scaleX = containerWidth / naturalWidth;
    const scaleY = containerHeight / naturalHeight;
    const scale = Math.max(scaleX, scaleY);
    img.style.width = (naturalWidth * scale) + 'px';
    img.style.height = (naturalHeight * scale) + 'px';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  showSlides();
});

window.addEventListener('load', adjustImageSizes);
