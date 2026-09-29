/**
 * Community Page Discussions Module (community.html)
 * Handles voting, discussion filters, modal thread creation, and bookmarking.
 */

document.addEventListener('DOMContentLoaded', function () {
  // Upvote handling
  document.addEventListener('click', function (e) {
    const voteBtn = e.target.closest('.btn-vote');
    if (voteBtn) {
      e.preventDefault();
      const countEl = voteBtn.parentElement.querySelector('.vote-count');
      if (!countEl) return;

      let count = parseInt(countEl.textContent, 10) || 0;
      const isVoted = voteBtn.classList.contains('voted');

      if (isVoted) {
        voteBtn.classList.remove('voted');
        countEl.textContent = count - 1;
      } else {
        voteBtn.classList.add('voted');
        countEl.textContent = count + 1;
        if (window.showToast) window.showToast('Upvote recorded!');
      }
    }

    // Thread Bookmark action
    const bookmarkBtn = e.target.closest('.btn-bookmark-thread');
    if (bookmarkBtn) {
      e.preventDefault();
      if (window.showToast) window.showToast('Thread bookmarked!');
    }
  });

  // Filter tabs
  const filterTabs = document.querySelectorAll('.community-filter-tabs .filter-pill');
  const forumCards = document.querySelectorAll('.forum-card');

  filterTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      filterTabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');

      const filterKey = tab.getAttribute('data-filter') || 'all';

      forumCards.forEach(function (card) {
        if (filterKey === 'all') {
          card.style.display = 'flex';
        } else {
          const text = card.textContent.toLowerCase();
          if (text.includes(filterKey.toLowerCase())) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        }
      });
    });
  });

  // Modal: Create Discussion
  const newDiscussionBtn = document.getElementById('btnNewDiscussion');
  const discussionModal = document.getElementById('createDiscussionModal');
  const newThreadForm = document.getElementById('newThreadForm');
  const communityFeed = document.getElementById('communityFeed');

  if (newDiscussionBtn && discussionModal) {
    newDiscussionBtn.addEventListener('click', function () {
      discussionModal.classList.add('active');
    });
  }

  if (newThreadForm && communityFeed) {
    newThreadForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const titleInput = document.getElementById('threadTitle');
      const catInput = document.getElementById('threadCategory');
      const bodyInput = document.getElementById('threadBody');

      const title = titleInput ? titleInput.value.trim() : '';
      const category = catInput ? catInput.value : 'Theories & Lore';
      const body = bodyInput ? bodyInput.value.trim() : '';

      if (!title || !body) {
        if (window.showToast) window.showToast('Please enter title and content', true);
        return;
      }

      const user = window.AuthContext ? window.AuthContext.getUser() : null;
      const username = user ? user.username : 'alex_prime';

      // Create new forum card
      const newCard = document.createElement('div');
      newCard.className = 'forum-card';
      newCard.innerHTML = `
        <div class="forum-vote-col">
          <button class="btn-vote" type="button" aria-label="Upvote">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
          </button>
          <span class="vote-count">1</span>
        </div>
        <div class="forum-body-col">
          <div class="forum-meta-bar">
            <span class="status-badge reviewing">${category}</span>
            <span>•</span>
            <span>@${username}</span>
            <span>•</span>
            <span>Just now</span>
          </div>
          <h3 class="forum-title">${title}</h3>
          <p class="forum-snippet">${body}</p>
          <div class="forum-action-bar">
            <span>0 comments</span>
            <span>•</span>
            <button type="button" class="btn-ghost btn-sm btn-bookmark-thread" style="padding:0; height:auto; color:var(--text-dim);">Save</button>
            <span>•</span>
            <button type="button" class="btn-ghost btn-sm" style="padding:0; height:auto; color:var(--text-dim);">Share</button>
          </div>
        </div>
      `;

      communityFeed.prepend(newCard);
      newThreadForm.reset();
      if (discussionModal) discussionModal.classList.remove('active');

      if (window.showToast) window.showToast('Discussion published successfully!');
    });
  }
});
