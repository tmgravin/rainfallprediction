const loginForm =document.querySelector('.login-form');
const registerForm = document.querySelector(".register-form");
const loginLink =document.querySelector(".login-link");
const registerLink =document.querySelector('.register-link');
const loginpopup =document.querySelector('.login-button');
const closepopup =document.querySelector('.close-button');
const wrapper =document.querySelector('.wrapper');


registerLink.addEventListener('click',()=>{
    loginForm.classList.remove("active");
    registerForm.classList.add("active");
});

loginLink.addEventListener("click",() =>{
 loginForm.classList.add("active");
 registerForm.classList.remove("active");
});

loginpopup.addEventListener('click',()=>{
    wrapper.classList.remove("invisible");
});
closepopup.addEventListener('click',()=>{
    wrapper.classList.add("invisible");
});

