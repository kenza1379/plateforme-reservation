// Toggle password visibility
function setupPasswordToggle(toggleId, inputId) {
    const toggle = document.getElementById(toggleId);
    const input = document.getElementById(inputId);
    
    if (toggle && input) {
        toggle.addEventListener('click', () => {
            const type = input.type === 'password' ? 'text' : 'password';
            input.type = type;
            toggle.classList.toggle('active');
        });
    }
}

setupPasswordToggle('passwordToggle', 'password');
setupPasswordToggle('confirmPasswordToggle', 'confirmPassword');

// Password strength checker
const passwordInput = document.getElementById('password');
const strengthContainer = document.getElementById('passwordStrength');
const strengthFill = document.getElementById('strengthFill');
const strengthText = document.getElementById('strengthText');

function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;

    return strength;
}

if (passwordInput && strengthContainer) {
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        if (password.length === 0) {
            strengthContainer.style.display = 'none';
            return;
        }

        strengthContainer.style.display = 'block';
        const strength = checkPasswordStrength(password);

        strengthFill.className = 'strength-fill';
        if (strength <= 1) {
            strengthFill.classList.add('weak');
            strengthText.textContent = 'Faible';
        } else if (strength <= 2) {
            strengthFill.classList.add('medium');
            strengthText.textContent = 'Moyen';
        } else {
            strengthFill.classList.add('strong');
            strengthText.textContent = 'Fort';
        }
    });
}

// Form validation (visuelle uniquement, vraie validation côté serveur)
const form = document.getElementById('signupForm');
const emailInput = document.getElementById('email');
const confirmPasswordInput = document.getElementById('confirmPassword');

function showError(inputId, message) {
    const errorElement = document.getElementById(inputId + 'Error');
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function clearError(inputId) {
    const errorElement = document.getElementById(inputId + 'Error');
    if (errorElement) {
        errorElement.textContent = '';
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Real-time validation
if (emailInput) {
    emailInput.addEventListener('blur', () => {
        if (emailInput.value && !validateEmail(emailInput.value)) {
            showError('email', 'Adresse email invalide');
        } else {
            clearError('email');
        }
    });
}

if (confirmPasswordInput && passwordInput) {
    confirmPasswordInput.addEventListener('input', () => {
        if (confirmPasswordInput.value && confirmPasswordInput.value !== passwordInput.value) {
            showError('confirmPassword', 'Les mots de passe ne correspondent pas');
        } else {
            clearError('confirmPassword');
        }
    });
}

// Afficher le loader au submit
if (form) {
    form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('.comfort-button');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
    });
}