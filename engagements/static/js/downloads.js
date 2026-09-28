/**
 * Offline Downloads & Storage Manager Module (downloads.html)
 */

document.addEventListener('DOMContentLoaded', function () {
  // Pause / Resume individual downloads
  document.addEventListener('click', function (e) {
    const pauseBtn = e.target.closest('.btn-toggle-download');
    if (pauseBtn) {
      e.preventDefault();
      const card = pauseBtn.closest('.download-item-card');
      if (!card) return;

      const statusText = card.querySelector('.download-status-indicator');
      const isPaused = pauseBtn.getAttribute('data-paused') === 'true';

      if (isPaused) {
        pauseBtn.setAttribute('data-paused', 'false');
        pauseBtn.textContent = 'Pause';
        if (statusText) {
          statusText.className = 'download-status-indicator status-text active';
          statusText.textContent = '• Downloading (12 MB/s)';
        }
      } else {
        pauseBtn.setAttribute('data-paused', 'true');
        pauseBtn.textContent = 'Resume';
        if (statusText) {
          statusText.className = 'download-status-indicator status-text paused';
          statusText.textContent = '• Paused';
        }
      }
    }

    // Delete download item
    const deleteBtn = e.target.closest('.btn-delete-download');
    if (deleteBtn) {
      e.preventDefault();
      const card = deleteBtn.closest('.download-item-card');
      if (card) {
        card.remove();
        if (window.showToast) window.showToast('Download removed from storage queue.');
      }
    }
  });

  // Pause All / Resume All
  const btnPauseAll = document.getElementById('btnPauseAllDownloads');
  let allPaused = false;

  if (btnPauseAll) {
    btnPauseAll.addEventListener('click', function () {
      allPaused = !allPaused;
      btnPauseAll.textContent = allPaused ? 'Resume All' : 'Pause All';

      document.querySelectorAll('.btn-toggle-download').forEach(function (btn) {
        const card = btn.closest('.download-item-card');
        const statusText = card ? card.querySelector('.download-status-indicator') : null;

        if (allPaused) {
          btn.setAttribute('data-paused', 'true');
          btn.textContent = 'Resume';
          if (statusText) {
            statusText.className = 'download-status-indicator status-text paused';
            statusText.textContent = '• Paused';
          }
        } else {
          btn.setAttribute('data-paused', 'false');
          btn.textContent = 'Pause';
          if (statusText) {
            statusText.className = 'download-status-indicator status-text active';
            statusText.textContent = '• Downloading (12 MB/s)';
          }
        }
      });

      if (window.showToast) {
        window.showToast(allPaused ? 'All downloads paused.' : 'All downloads resumed.');
      }
    });
  }

  // Storage Cleaner
  const btnCleanCache = document.getElementById('btnCleanCache');
  const storageUsageText = document.getElementById('storageUsageText');
  const barVideo = document.getElementById('storageBarVideo');
  const barAudio = document.getElementById('storageBarAudio');

  if (btnCleanCache) {
    btnCleanCache.addEventListener('click', function () {
      if (storageUsageText) {
        storageUsageText.textContent = '0.0 GB used of 128 GB';
      }
      if (barVideo) barVideo.style.width = '0%';
      if (barAudio) barAudio.style.width = '0%';

      if (window.showToast) {
        window.showToast('Storage cleaner complete: 53.8 GB cache cleared.');
      }
    });
  }

  // Offline Player Modal
  const offlinePlayerModal = document.getElementById('offlinePlayerModal');
  const offlinePlayBtns = document.querySelectorAll('.btn-play-offline');
  const offlinePlayPauseBtn = document.getElementById('btnOfflinePlayPause');
  const offlineTitle = document.getElementById('offlinePlayerTitle');

  offlinePlayBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const title = btn.getAttribute('data-title') || 'Offline Episode';
      if (offlineTitle) offlineTitle.textContent = title;
      if (offlinePlayerModal) offlinePlayerModal.classList.add('active');
    });
  });

  if (offlinePlayPauseBtn) {
    offlinePlayPauseBtn.addEventListener('click', function () {
      const isPlaying = offlinePlayPauseBtn.getAttribute('data-playing') === 'true';
      if (isPlaying) {
        offlinePlayPauseBtn.setAttribute('data-playing', 'false');
        offlinePlayPauseBtn.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        `;
      } else {
        offlinePlayPauseBtn.setAttribute('data-playing', 'true');
        offlinePlayPauseBtn.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16"></rect>
            <rect x="14" y="4" width="4" height="16"></rect>
          </svg>
        `;
      }
    });
  }
});
