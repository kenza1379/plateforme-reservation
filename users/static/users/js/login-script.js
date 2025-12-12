// Tout le code doit être à l'intérieur de DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');

    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            passwordToggle.classList.toggle('active');
        });
    }

    // Fonctions de gestion des erreurs
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

    // Validation en temps réel pour l'UX
    const identifierInput = document.getElementById('identifier');
    if (identifierInput) {
        identifierInput.addEventListener('blur', () => {
            // Vérifier si c'est un email et le valider
            if (identifierInput.value && identifierInput.value.includes('@')) {
                if (!validateEmail(identifierInput.value)) {
                    showError('identifier', 'Adresse email invalide');
                } else {
                    clearError('identifier');
                }
            } else {
                clearError('identifier');
            }
        });
    }

    // Afficher le loader au submit
    const form = document.getElementById('loginForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('.comfort-button');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    }

    // Gestion du modal "Mot de passe oublié"
    const modal = document.getElementById('resetPasswordModal');
    const openBtn = document.getElementById('forgotPasswordLink');
    const closeBtn = document.getElementById('closeModal');
    const resetForm = modal ? modal.querySelector('form') : null;

    console.log('Modal éléments:', { modal, openBtn, closeBtn, resetForm });

    if (openBtn && modal) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Ouverture du modal');
            modal.style.display = 'flex';
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', function() {
            console.log('Fermeture du modal');
            modal.style.display = 'none';
        });
    }

    // Fermer le modal en cliquant à l'extérieur
    if (modal) {
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                console.log('Clic en dehors du modal');
                modal.style.display = 'none';
            }
        });
    }

    // Déboguer la soumission du formulaire
    if (resetForm) {
        resetForm.addEventListener('submit', function(e) {
            console.log('Formulaire de réinitialisation soumis !');
            const email = resetForm.querySelector('input[name="email"]').value;
            console.log('Email:', email);
            // Ne pas empêcher la soumission
        });
    }
});