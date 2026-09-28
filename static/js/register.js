/**
 * Multi-Step Registration Wizard Module (register.html)
 */

document.addEventListener('DOMContentLoaded', function () {
  let currentStep = 1;
  const maxSteps = 4;
  let highestCompletedStep = 0;

  // Selected Preferences State
  let selectedTheme = 'dark';
  let selectedFontSize = 'standard';
  let selectedCategories = ['Anime'];

  // DOM Elements
  const stepPanes = document.querySelectorAll('.wizard-step-pane');
  const stepNodes = document.querySelectorAll('.stepper-node');
  const progressFill = document.getElementById('stepperProgressFill');
  const btnPrev = document.getElementById('btnPrevStep');
  const btnNext = document.getElementById('btnNextStep');
  const btnSubmit = document.getElementById('btnSubmitRegister');

  // Step 1 Inputs
  const regUsername = document.getElementById('regUsername');
  const regFirstName = document.getElementById('regFirstName');
  const regLastName = document.getElementById('regLastName');
  const regEmail = document.getElementById('regEmail');
  const regPassword = document.getElementById('regPassword');
  const togglePassBtn = document.getElementById('toggleRegPassword');

  // Step 2 Inputs
  const regBio = document.getElementById('regBio');
  const bioCount = document.getElementById('bioCount');

  // Step 4 Terms
  const agreeTerms = document.getElementById('agreeTerms');
  const reviewContainer = document.getElementById('reviewSummaryContainer');

  // Password toggle
  if (togglePassBtn && regPassword) {
    togglePassBtn.addEventListener('click', function () {
      const isPass = regPassword.getAttribute('type') === 'password';
      regPassword.setAttribute('type', isPass ? 'text' : 'password');
      togglePassBtn.setAttribute('aria-pressed', isPass ? 'true' : 'false');
      togglePassBtn.setAttribute('aria-label', isPass ? 'Hide password' : 'Show password');
      const iconPath = isPass
        ? '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>'
        : '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
      const svg = togglePassBtn.querySelector('svg');
      if (svg) svg.innerHTML = iconPath;
    });
  }

  // Live bio counter
  if (regBio && bioCount) {
    regBio.addEventListener('input', function () {
      if (regBio.value.length > 200) {
        regBio.value = regBio.value.substring(0, 200);
      }
      bioCount.textContent = regBio.value.length;
    });
  }

  // Theme selection cards
  document.querySelectorAll('.theme-card').forEach(function (card) {
    card.addEventListener('click', function () {
      document.querySelectorAll('.theme-card').forEach(function (c) { c.classList.remove('selected'); });
      card.classList.add('selected');
      selectedTheme = card.getAttribute('data-theme') || 'dark';
    });
  });

  // Font size selection cards
  document.querySelectorAll('.font-size-card').forEach(function (card) {
    card.addEventListener('click', function () {
      document.querySelectorAll('.font-size-card').forEach(function (c) { c.classList.remove('selected'); });
      card.classList.add('selected');
      selectedFontSize = card.getAttribute('data-font') || 'standard';
    });
  });

  // Category select chips
  document.querySelectorAll('.cat-select-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      chip.classList.toggle('selected');
      const cat = chip.getAttribute('data-cat');
      if (chip.classList.contains('selected')) {
        if (!selectedCategories.includes(cat)) selectedCategories.push(cat);
      } else {
        selectedCategories = selectedCategories.filter(function (c) { return c !== cat; });
      }
    });
  });

  function updateWizardUI() {
    // Show current pane
    stepPanes.forEach(function (pane) {
      const step = parseInt(pane.getAttribute('data-step'), 10);
      if (step === currentStep) {
        pane.classList.add('active');
      } else {
        pane.classList.remove('active');
      }
    });

    // Update stepper nodes
    stepNodes.forEach(function (node) {
      const step = parseInt(node.getAttribute('data-step'), 10);
      node.classList.remove('active', 'completed', 'clickable');

      if (step === currentStep) {
        node.classList.add('active');
      } else if (step <= highestCompletedStep) {
        node.classList.add('completed', 'clickable');
      }
    });

    // Progress bar fill: 0%, 33.3%, 66.6%, 100%
    if (progressFill) {
      const percentage = ((currentStep - 1) / (maxSteps - 1)) * 100;
      progressFill.style.width = percentage + '%';
    }

    // Buttons visibility
    if (btnPrev) {
      btnPrev.style.display = currentStep > 1 ? 'inline-flex' : 'none';
    }
    if (btnNext) {
      btnNext.style.display = currentStep < maxSteps ? 'inline-flex' : 'none';
    }
    if (btnSubmit) {
      btnSubmit.style.display = currentStep === maxSteps ? 'inline-flex' : 'none';
    }

    // Populate Review Step
    if (currentStep === 4 && reviewContainer) {
      reviewContainer.innerHTML = `
        <div class="review-summary-row">
          <span class="review-summary-label">Full Name</span>
          <span class="review-summary-value">${regFirstName ? regFirstName.value : ''} ${regLastName ? regLastName.value : ''}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Username</span>
          <span class="review-summary-value">@${regUsername ? regUsername.value : ''}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Email</span>
          <span class="review-summary-value">${regEmail ? regEmail.value : ''}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Bio</span>
          <span class="review-summary-value">${(regBio && regBio.value) ? regBio.value : 'No bio provided'}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Preferred Theme</span>
          <span class="review-summary-value" style="text-transform: capitalize;">${selectedTheme}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Font Scale</span>
          <span class="review-summary-value" style="text-transform: capitalize;">${selectedFontSize}</span>
        </div>
        <div class="review-summary-row">
          <span class="review-summary-label">Favorite Fandoms</span>
          <span class="review-summary-value">${selectedCategories.join(', ') || 'None selected'}</span>
        </div>
      `;
    }
  }

  function validateCurrentStep() {
    if (currentStep === 1) {
      const u = regUsername ? regUsername.value.trim() : '';
      const em = regEmail ? regEmail.value.trim() : '';
      const p = regPassword ? regPassword.value : '';

      if (u.length < 3) {
        if (window.showToast) window.showToast('Username must be at least 3 characters', true);
        return false;
      }
      if (!em.includes('@') || !em.includes('.')) {
        if (window.showToast) window.showToast('Please enter a valid email address', true);
        return false;
      }
      if (p.length < 6) {
        if (window.showToast) window.showToast('Password must be at least 6 characters', true);
        return false;
      }
      return true;
    }

    if (currentStep === 2) {
      // Bio is optional, but <= 200 chars
      if (regBio && regBio.value.length > 200) {
        if (window.showToast) window.showToast('Bio cannot exceed 200 characters', true);
        return false;
      }
      return true;
    }

    if (currentStep === 3) {
      if (selectedCategories.length === 0) {
        if (window.showToast) window.showToast('Please select at least 1 favorite category', true);
        return false;
      }
      return true;
    }

    if (currentStep === 4) {
      if (agreeTerms && !agreeTerms.checked) {
        if (window.showToast) window.showToast('You must agree to the Community Guidelines & Terms', true);
        return false;
      }
      return true;
    }

    return true;
  }

  // Stepper Node Clicks (jump back to completed steps)
  stepNodes.forEach(function (node) {
    node.addEventListener('click', function () {
      const targetStep = parseInt(node.getAttribute('data-step'), 10);
      if (targetStep <= highestCompletedStep) {
        currentStep = targetStep;
        updateWizardUI();
      }
    });
  });

  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (validateCurrentStep()) {
        if (currentStep > highestCompletedStep) {
          highestCompletedStep = currentStep;
        }
        currentStep++;
        updateWizardUI();
      }
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      if (currentStep > 1) {
        currentStep--;
        updateWizardUI();
      }
    });
  }

  // Complete Registration Form Submit
  const regForm = document.getElementById('registerForm');
  if (regForm) {
    regForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validateCurrentStep()) return;

      const userProfile = {
        username: regUsername.value.trim(),
        firstName: regFirstName ? regFirstName.value.trim() : 'Alex',
        lastName: regLastName ? regLastName.value.trim() : '',
        email: regEmail.value.trim(),
        bio: regBio ? regBio.value.trim() : '',
        preferredTheme: selectedTheme,
        fontSize: selectedFontSize,
        favoriteCategories: selectedCategories
      };

      // Persist to fanhub_user
      localStorage.setItem('fanhub_user', JSON.stringify(userProfile));
      localStorage.setItem('fanhub_theme', selectedTheme);
      localStorage.setItem('fanhub_fontsize', selectedFontSize);

      // Create session in AuthContext
      if (window.AuthContext) {
        window.AuthContext.login({
          username: userProfile.username,
          firstName: userProfile.firstName,
          lastName: userProfile.lastName,
          email: userProfile.email,
          tier: 'Founding Member'
        });
      }

      if (window.showToast) {
        window.showToast('Welcome to Fan Hub+! Account created successfully.');
      }

      // Check ?next=
      const urlParams = new URLSearchParams(window.location.search);
      const nextDest = urlParams.get('next') || '../index.html';

      setTimeout(function () {
        window.location.href = nextDest;
      }, 500);
    });
  }

  updateWizardUI();
});
