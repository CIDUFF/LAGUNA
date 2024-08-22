const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});


document.addEventListener("DOMContentLoaded", function() {
  const questions = document.querySelectorAll('.faq-question');
  
  questions.forEach(question => {
      question.addEventListener('click', () => {
          const answer = question.nextElementSibling;
          if (answer.style.display === 'block') {
              answer.style.display = 'none';
          } else {
              answer.style.display = 'block';
          }
      });
  });
});