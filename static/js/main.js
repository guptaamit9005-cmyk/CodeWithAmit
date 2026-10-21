// Student Success Hub - Main JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Initialization: Exclusively Pure White UI
    const htmlElement = document.documentElement;
    htmlElement.setAttribute('data-bs-theme', 'light');
    localStorage.setItem('ssh_theme', 'light');

    // 2. Auto-dismiss alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        });
    }, 5000);

    // 3. Copy Code Block Buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            let textToCopy = '';
            if (targetId) {
                const targetEl = document.getElementById(targetId);
                textToCopy = targetEl ? (targetEl.value || targetEl.innerText) : '';
            } else {
                const pre = btn.closest('.code-container')?.querySelector('pre code') || btn.closest('.card')?.querySelector('code');
                textToCopy = pre ? pre.innerText : '';
            }

            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalHtml = btn.innerHTML;
                    btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                    btn.classList.add('btn-success');
                    btn.classList.remove('btn-outline-light', 'btn-outline-secondary');
                    setTimeout(() => {
                        btn.innerHTML = originalHtml;
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-outline-light');
                    }, 2000);
                }).catch(err => {
                    console.error('Copy failed:', err);
                });
            }
        });
    });

    // 4. Code Editor Tab Key handling in textareas
    document.querySelectorAll('.code-editor-textarea').forEach(textarea => {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    });

    // 5. Roadmap Topic Toggle via AJAX
    document.querySelectorAll('.topic-check-input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const topicId = this.getAttribute('data-topic-id');
            const roadmapSlug = this.getAttribute('data-roadmap-slug');
            const isChecked = this.checked;

            fetch(`/roadmaps/${roadmapSlug}/toggle-topic/${topicId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ is_completed: isChecked })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const progressBar = document.getElementById('roadmap-progress-bar');
                    const progressText = document.getElementById('roadmap-progress-text');
                    if (progressBar && data.completion_percent !== undefined) {
                        progressBar.style.width = `${data.completion_percent}%`;
                        progressBar.setAttribute('aria-valuenow', data.completion_percent);
                    }
                    if (progressText && data.completion_percent !== undefined) {
                        progressText.innerText = `${data.completion_percent}% Complete`;
                    }
                    // Visual state toggle on topic row
                    const topicRow = document.getElementById(`topic-row-${topicId}`);
                    if (topicRow) {
                        if (isChecked) {
                            topicRow.classList.add('topic-completed');
                        } else {
                            topicRow.classList.remove('topic-completed');
                        }
                    }
                }
            })
            .catch(err => console.error('Error toggling topic progress:', err));
        });
    });
});

// Helper: Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
