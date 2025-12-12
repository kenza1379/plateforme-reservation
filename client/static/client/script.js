// ========================================
// GESTION DES MODALS
// ========================================

// Ouvrir un modal
function openModal(id) {
  console.log(`🔓 Ouverture modal: ${id}`);
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("active");
}

// Fermer un modal
function closeModal(id) {
  console.log(`🔒 Fermeture modal: ${id}`);
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("active");
}

// ========================================
// EVENTS GLOBAUX
// ========================================
document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ Script chargé");

  // Ouvrir modals via data-target
  document.addEventListener("click", function (e) {
    const targetBtn = e.target.closest("[data-target]");
    if (targetBtn) {
      const id = targetBtn.getAttribute("data-target");
      if (id) openModal(id);
      e.preventDefault();
    }
  });

  // Fermer via data-close
  document.addEventListener("click", function (e) {
    const closeBtn = e.target.closest("[data-close]");
    if (closeBtn) {
      const id = closeBtn.getAttribute("data-close");
      
      if (id) {
        closeModal(id);
      } else {
        // Si pas d'ID → fermer le modal parent
        const modal = closeBtn.closest(".modal-custom");
        if (modal) modal.classList.remove("active");
      }
      e.preventDefault();
    }
  });

  // Fermer en cliquant sur l'overlay
  window.onclick = function (e) {
    if (e.target.classList.contains("modal-custom")) {
      e.target.classList.remove("active");
      console.log("🔒 Fermé via overlay");
    }
  };

  // ========================================
  // PHOTO DE PROFIL CLIQUABLE
  // ========================================
  const photo = document.querySelector(".profile-photo");
  if (photo) {
    photo.addEventListener("click", () => {
      const id = photo.getAttribute("data-target");
      if (id) openModal(id);
    });
  }

  // ========================================
  // DARK MODE
  // ========================================
  const themeButton = document.getElementById("theme-toggle");
  if (themeButton) {
    themeButton.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      themeButton.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
      localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
    });

    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
      themeButton.textContent = "☀️";
    }
  }
});
