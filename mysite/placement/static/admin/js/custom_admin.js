// Custom Admin JavaScript for Student Model

document.addEventListener('DOMContentLoaded', function() {
    // Add custom class to body for styling
    document.body.classList.add('admin-student');

    // Highlight top 5 students
    highlightTopStudents();

    // Add total count display
    addTotalCount();

    // Enhance search functionality
    enhanceSearch();

    // Add tooltips for colored badges
    addTooltips();

    // Auto-refresh stats every 30 seconds
    setInterval(updateStats, 30000);
});

function highlightTopStudents() {
    const rows = document.querySelectorAll('.results table tbody tr');
    const topStudents = Array.from(rows).slice(0, 5);

    topStudents.forEach((row, index) => {
        row.style.background = `linear-gradient(90deg, rgba(16, 185, 129, ${0.1 - index * 0.015}), rgba(30, 41, 59, 0.3))`;
        row.style.borderLeft = `4px solid #10b981`;

        // Add crown icon to first place
        if (index === 0) {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell) {
                firstCell.innerHTML = '👑 ' + firstCell.innerHTML;
            }
        }
    });
}

function addTotalCount() {
    const changelistForm = document.querySelector('.changelist-form');
    if (changelistForm) {
        const totalCountDiv = document.createElement('div');
        totalCountDiv.className = 'total-count';
        totalCountDiv.innerHTML = `
            <span style="font-size: 1.5em;">📊</span>
            Total Students: <span id="total-count">${getTotalCount()}</span>
        `;
        changelistForm.parentNode.insertBefore(totalCountDiv, changelistForm);
    }
}

function getTotalCount() {
    // This would ideally come from Django context, but for now we'll count visible rows
    const rows = document.querySelectorAll('.results table tbody tr');
    return rows.length;
}

function enhanceSearch() {
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.placeholder = '🔍 Search by name, email, or skills...';

        // Add real-time search feedback
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const rows = document.querySelectorAll('.results table tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(query) || query === '') {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

function addTooltips() {
    // Add tooltips to colored badges
    const badges = document.querySelectorAll('.colored-badge');
    badges.forEach(badge => {
        badge.title = 'Click to view details';
        badge.style.cursor = 'pointer';
    });
}

function updateStats() {
    // Update total count if pagination changes
    const totalCountElement = document.getElementById('total-count');
    if (totalCountElement) {
        totalCountElement.textContent = getTotalCount();
    }

    // Refresh highlights
    highlightTopStudents();
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+F focuses search
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.querySelector('#searchbar');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Ctrl+R refreshes the page
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        location.reload();
    }
});

// Add loading animation for bulk actions
const actionSelect = document.querySelector('#action-toggle');
if (actionSelect) {
    actionSelect.addEventListener('change', function() {
        if (this.value) {
            const submitButton = document.querySelector('button[name="index"]');
            if (submitButton) {
                submitButton.innerHTML = '⏳ Processing...';
                submitButton.disabled = true;
            }
        }
    });
}

// Auto-save inline edits
let editTimeout;
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('inline-edit')) {
        clearTimeout(editTimeout);
        editTimeout = setTimeout(() => {
            // Here you could add AJAX auto-save functionality
            console.log('Auto-saving:', e.target.name, e.target.value);
        }, 1000);
    }
});