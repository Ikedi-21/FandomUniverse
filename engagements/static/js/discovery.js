/**
 * Discovery Multiverse Matrix Module (explore.html)
 * Reads URL search query ?q=, handles discovery filter matrix.
 */

document.addEventListener('DOMContentLoaded', function () {
  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get('q');
  const cards = document.querySelectorAll('.discovery-card, .trending-card');
  const filterPills = document.querySelectorAll('.discovery-filters .filter-pill');

  function applyFilter(categoryKey) {
    cards.forEach(function (card) {
      if (!categoryKey || categoryKey === 'all') {
        card.style.display = '';
      } else {
        const text = card.textContent.toLowerCase();
        if (text.includes(categoryKey.toLowerCase())) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      }
    });
  }

  // Handle URL param
  if (initialQuery) {
    const searchInput = document.getElementById('globalSearchInput');
    if (searchInput) searchInput.value = initialQuery;

    cards.forEach(function (card) {
      const text = card.textContent.toLowerCase();
      if (text.includes(initialQuery.toLowerCase())) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });

    if (window.showToast) {
      window.showToast(`Filtering results for "${initialQuery}"`);
    }
  }

  // Filter Pills
  filterPills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      filterPills.forEach(function (p) { p.classList.remove('active'); });
      pill.classList.add('active');

      const filterKey = pill.getAttribute('data-filter') || 'all';
      applyFilter(filterKey);
    });
  });
});
