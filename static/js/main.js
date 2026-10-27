/**
 * main.js - Client-Side Interactive Logic for ShopEase
 * Includes toast alerts, quantity updates, confirmation dialogs, and demo autofill.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      });
    }

    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    }, 5000);
  });

  // 2. Quantity Selector Controls
  document.querySelectorAll('.qty-control').forEach(control => {
    const minusBtn = control.querySelector('.qty-minus');
    const plusBtn = control.querySelector('.qty-plus');
    const input = control.querySelector('.qty-input');

    if (minusBtn && plusBtn && input) {
      minusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          // Trigger change event if inside a form that auto-submits
          input.dispatchEvent(new Event('change'));
        }
      });

      plusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        let max = parseInt(input.getAttribute('max')) || 999;
        if (val < max) {
          input.value = val + 1;
          input.dispatchEvent(new Event('change'));
        }
      });
    }
  });

  // 3. Password Visibility Toggle
  document.querySelectorAll('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
          input.type = 'password';
          btn.innerHTML = '<i class="bi bi-eye"></i>';
        }
      }
    });
  });

  // 4. Quick-fill Demo Credentials (Academic presentation helper)
  window.fillCredentials = function(email, password) {
    const emailField = document.getElementById('login-email');
    const pwField = document.getElementById('login-password');
    if (emailField && pwField) {
      emailField.value = email;
      pwField.value = password;
      emailField.focus();
    }
  };

  // 5. Add to Cart with AJAX and Toast Feedback
  document.querySelectorAll('.ajax-add-cart').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const actionUrl = form.getAttribute('action');
      const formData = new FormData(form);

      try {
        const response = await fetch(actionUrl, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        });

        const result = await response.json();
        if (result.success) {
          // Update cart badge
          const badge = document.querySelector('.badge-count');
          if (badge) {
            badge.textContent = result.cart_count;
            badge.style.display = result.cart_count > 0 ? 'inline-block' : 'none';
          }
          showToast(result.message, 'success');
        } else {
          showToast(result.message || 'Could not add product', 'danger');
        }
      } catch (err) {
        // Fallback to standard submit if fetch fails
        form.submit();
      }
    });
  });

  // 6. Generic Toast Notification Builder
  window.showToast = function(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.position = 'fixed';
      container.style.bottom = '20px';
      container.style.right = '20px';
      container.style.zIndex = '99999';
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.gap = '10px';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.margin = '0';
    toast.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.2)';
    toast.style.minWidth = '280px';
    toast.innerHTML = `
      <span>${message}</span>
      <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  };
});
