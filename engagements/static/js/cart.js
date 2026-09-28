/**
 * Shopping Cart Module (goodies.html & global)
 * Serializes cart array to localStorage: fanhub_cart = [{title, price, img}]
 */

(function () {
  'use strict';

  const CART_KEY = 'fanhub_cart';

  function getCart() {
    try {
      const data = localStorage.getItem(CART_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateCartUI();
  }

  function updateCartUI() {
    const cart = getCart();
    const count = cart.length;

    // Badges
    const badges = document.querySelectorAll('#cartCountBadge, .cart-count-badge');
    badges.forEach(function (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    });

    // Drawer list
    const itemsContainer = document.getElementById('cartDrawerItems');
    const subtotalEl = document.getElementById('cartSubtotalAmount');

    if (itemsContainer) {
      if (count === 0) {
        itemsContainer.innerHTML = `
          <div style="text-align: center; padding: 40px 20px; color: var(--text-dim);">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin: 0 auto 12px; color: var(--text-dim);">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
            <p style="font-weight: var(--fw-semibold);">Your bag is empty</p>
            <p style="font-size: var(--font-sm); margin-top: 4px;">Discover exclusive collectibles and merchandise.</p>
          </div>
        `;
      } else {
        let html = '';
        let total = 0;

        cart.forEach(function (item, index) {
          const priceNum = parseFloat(item.price.replace(/[^0-9.]/g, '')) || 0;
          total += priceNum;

          html += `
            <div class="cart-item-row" data-cart-index="${index}">
              <img src="${item.img}" alt="${item.title}" class="cart-item-thumb" />
              <div class="cart-item-info">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-price">${item.price}</div>
              </div>
              <button type="button" class="cart-item-remove" data-remove-index="${index}" aria-label="Remove item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
          `;
        });

        itemsContainer.innerHTML = html;

        // Attach remove events
        itemsContainer.querySelectorAll('[data-remove-index]').forEach(function (btn) {
          btn.addEventListener('click', function () {
            const idx = parseInt(btn.getAttribute('data-remove-index'), 10);
            removeFromCart(idx);
          });
        });

        if (subtotalEl) {
          subtotalEl.textContent = '$' + total.toFixed(2);
        }
      }

      if (count === 0 && subtotalEl) {
        subtotalEl.textContent = '$0.00';
      }
    }
  }

  function addToCart(title, price, img) {
    const cart = getCart();
    cart.push({ title: title, price: price, img: img });
    saveCart(cart);
    if (window.showToast) {
      window.showToast(`Added ${title} (${price}) to your cart!`);
    }
  }

  function removeFromCart(index) {
    const cart = getCart();
    if (index >= 0 && index < cart.length) {
      const removed = cart.splice(index, 1)[0];
      saveCart(cart);
      if (window.showToast) {
        window.showToast(`Removed ${removed.title} from cart.`);
      }
    }
  }

  function checkout() {
    const cart = getCart();
    if (cart.length === 0) {
      if (window.showToast) window.showToast('Your bag is empty!', true);
      return;
    }

    const orderNum = 'FAN-' + Math.floor(10000 + Math.random() * 90000);
    localStorage.setItem(CART_KEY, JSON.stringify([]));
    updateCartUI();

    const drawerOverlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    if (drawerOverlay) drawerOverlay.classList.remove('active');
    if (drawer) drawer.classList.remove('open');

    if (window.showToast) {
      window.showToast(`Order confirmed #${orderNum}! Receipt sent to email.`);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    updateCartUI();

    // Trigger cart drawer open
    const cartBtn = document.getElementById('headerCartBtn');
    const drawerOverlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    const closeDrawerBtn = document.getElementById('closeCartDrawerBtn');

    if (cartBtn && drawerOverlay && drawer) {
      cartBtn.addEventListener('click', function (e) {
        e.preventDefault();
        drawerOverlay.classList.add('active');
        drawer.classList.add('open');
      });
    }

    if (closeDrawerBtn && drawerOverlay && drawer) {
      closeDrawerBtn.addEventListener('click', function () {
        drawerOverlay.classList.remove('active');
        drawer.classList.remove('open');
      });
    }

    if (drawerOverlay && drawer) {
      drawerOverlay.addEventListener('click', function (e) {
        if (e.target === drawerOverlay) {
          drawerOverlay.classList.remove('active');
          drawer.classList.remove('open');
        }
      });
    }

    // "Add to Bag" buttons on product cards
    document.querySelectorAll('.btn-add-cart').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const card = btn.closest('.product-card');
        if (!card) return;

        const titleEl = card.querySelector('.product-title');
        const priceEl = card.querySelector('.product-price');
        const imgEl = card.querySelector('.product-img-wrap img');

        const title = titleEl ? titleEl.textContent.trim() : 'Fandom Collectible';
        const price = priceEl ? priceEl.textContent.trim() : '$49.99';
        const img = imgEl ? imgEl.src : '../images/posters/demon_slayer_thumb.jpg';

        addToCart(title, price, img);
      });
    });

    // Checkout button
    const checkoutBtn = document.getElementById('btnCartCheckout');
    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', function () {
        checkout();
      });
    }
  });

  window.Cart = {
    getCart: getCart,
    addToCart: addToCart,
    removeFromCart: removeFromCart,
    checkout: checkout
  };
})();
