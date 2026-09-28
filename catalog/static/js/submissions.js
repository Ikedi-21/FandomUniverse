/**
 * Creator Studio & Submissions Module (submissions.html)
 */

document.addEventListener('DOMContentLoaded', function () {
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('hiddenFileInput');
  const filePreview = document.getElementById('uploadFilePreview');
  const form = document.getElementById('creatorSubmissionForm');
  const btnSaveDraft = document.getElementById('btnSaveDraft');
  const submissionsTable = document.getElementById('submissionsTableBody');

  // Stats counters
  const totalSubmissionsEl = document.getElementById('statTotalSubmissions');
  const inReviewEl = document.getElementById('statInReview');

  // Dropzone click & drag
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', function () {
      fileInput.click();
    });

    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        const sizeMb = (file.size / (1024 * 1024)).toFixed(1);

        if (filePreview) {
          filePreview.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; color: var(--color-green);">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <div>
                <strong style="color: var(--text-main);">${file.name}</strong> (${sizeMb} MB) • <span style="color: var(--text-dim);">${file.type || 'Media File'}</span>
              </div>
            </div>
          `;
        }
      }
    });
  }

  // Save Draft
  if (btnSaveDraft) {
    btnSaveDraft.addEventListener('click', function () {
      const title = document.getElementById('subTitle') ? document.getElementById('subTitle').value : '';
      const desc = document.getElementById('subDescription') ? document.getElementById('subDescription').value : '';

      const draft = {
        title: title,
        desc: desc,
        date: new Date().toISOString()
      };

      localStorage.setItem('fanhub_creator_draft', JSON.stringify(draft));
      if (window.showToast) {
        window.showToast('Draft saved successfully to local storage.');
      }
    });
  }

  // Submit form
  if (form && submissionsTable) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const titleInput = document.getElementById('subTitle');
      const catInput = document.getElementById('subCategory');

      const title = titleInput ? titleInput.value.trim() : '';
      const category = catInput ? catInput.value : 'Anime Clip';

      if (!title) {
        if (window.showToast) window.showToast('Please enter a submission title', true);
        return;
      }

      const now = new Date();
      const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

      const newRow = document.createElement('tr');
      newRow.style.borderBottom = '1px solid var(--border-subtle)';
      newRow.innerHTML = `
        <td style="padding: 14px 16px; font-weight: var(--fw-semibold);">${title}</td>
        <td style="padding: 14px 16px; color: var(--text-dim);">${category}</td>
        <td style="padding: 14px 16px;"><span class="status-badge reviewing">Reviewing</span></td>
        <td style="padding: 14px 16px; color: var(--text-dim);">0</td>
        <td style="padding: 14px 16px; color: var(--text-dim);">${dateStr}</td>
        <td style="padding: 14px 16px; text-align: right;">
          <button type="button" class="btn btn-ghost btn-sm btn-delete-submission" style="color: #ef4444;" aria-label="Delete"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>
        </td>
      `;

      submissionsTable.prepend(newRow);

      // Increment counters
      if (totalSubmissionsEl) {
        let count = parseInt(totalSubmissionsEl.textContent, 10) || 8;
        totalSubmissionsEl.textContent = count + 1;
      }
      if (inReviewEl) {
        let count = parseInt(inReviewEl.textContent, 10) || 2;
        inReviewEl.textContent = count + 1;
      }

      form.reset();
      if (filePreview) {
        filePreview.innerHTML = `
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-dim); margin: 0 auto 8px;">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <div style="font-weight: var(--fw-bold); font-size: var(--font-base);">Drop files to upload or browse</div>
          <div style="font-size: var(--font-xs); color: var(--text-dim);">MP4, MOV, WebM, PNG, JPG - Up to 2.5 GB</div>
        `;
      }

      if (window.showToast) {
        window.showToast('Submission uploaded and queued for editorial review!');
      }
    });
  }

  // Row Actions: Stats and Delete
  const statsModal = document.getElementById('statsModal');

  document.addEventListener('click', function (e) {
    if (e.target.closest('.btn-view-stats')) {
      e.preventDefault();
      if (statsModal) statsModal.classList.add('active');
    }

    const deleteBtn = e.target.closest('.btn-delete-submission');
    if (deleteBtn) {
      e.preventDefault();
      const row = deleteBtn.closest('tr');
      if (row) {
        row.remove();
        if (totalSubmissionsEl) {
          let count = parseInt(totalSubmissionsEl.textContent, 10) || 1;
          if (count > 0) totalSubmissionsEl.textContent = count - 1;
        }
        if (window.showToast) {
          window.showToast('Submission deleted.');
        }
      }
    }
  });

  const btnCopyStatsLink = document.getElementById('btnCopyStatsLink');
  if (btnCopyStatsLink) {
    btnCopyStatsLink.addEventListener('click', function () {
      if (window.showToast) window.showToast('Analytics link copied to clipboard!');
    });
  }
});
