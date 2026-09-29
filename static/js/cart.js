/* Merchandise is display-only. No browser cart, checkout, order, or payment behavior. */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.btn-add-cart, #btnCartCheckout, #headerCartBtn').forEach(function (button) {
    button.disabled = true;
    button.setAttribute('aria-disabled', 'true');
    button.title = 'Merchandise is display-only.';
    if (button.classList.contains('btn-add-cart')) button.textContent = 'Display only';
    if (button.id === 'btnCartCheckout' || button.id === 'headerCartBtn') button.hidden = true;
  });
  document.querySelectorAll('#cartDrawer, #cartDrawerOverlay').forEach(function (drawer) {
    drawer.hidden = true;
  });
});
