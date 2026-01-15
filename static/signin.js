document.getElementById('year').textContent = new Date().getFullYear();

const togglePassword = document.getElementById('toggle-password');
const passwordInput = document.getElementById('password');

togglePassword.addEventListener('click', () => {
  const type = passwordInput.type === 'password' ? 'text' : 'password';
  passwordInput.type = type;
  togglePassword.innerHTML = type === 'password'
    ? '<i class="bi bi-eye-fill"></i>'
    : '<i class="bi bi-eye-slash-fill"></i>';
});

const form = document.getElementById('login-form');
const loginButton = document.getElementById('login-button');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');

function showError(message) {
  errorText.textContent = message;
  errorMessage.classList.remove('d-none');
}

function hideError() {
  errorMessage.classList.add('d-none');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!email || !password) {
    showError('Please enter both email and password');
    return;
  }

  loginButton.disabled = true;
  loginButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';

  form.submit();
});
