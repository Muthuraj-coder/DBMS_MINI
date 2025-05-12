/**
 * Student Information System
 * Main JavaScript file for the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Setup confirmation dialogs
    setupConfirmationDialogs();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup datatables
    setupDataTables();
});

/**
 * Setup confirmation dialogs for delete actions
 */
function setupConfirmationDialogs() {
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
            const confirmButton = document.getElementById('confirmDeleteButton');
            const form = this.closest('form');
            
            document.getElementById('deleteItemName').textContent = this.getAttribute('data-item-name') || 'this item';
            
            confirmButton.onclick = function() {
                form.submit();
            };
            
            confirmModal.show();
        });
    });
}

/**
 * Setup client-side form validation
 */
function setupFormValidation() {
    // Fetch all forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Setup DataTables for enhanced table functionality
 */
function setupDataTables() {
    document.querySelectorAll('.datatable').forEach(table => {
        $(table).DataTable({
            responsive: true,
            pageLength: 10,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search..."
            },
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        });
    });
}

/**
 * Toggle password visibility
 */
function togglePasswordVisibility(inputId) {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = document.querySelector(`#${inputId} + .input-group-text i`);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('bi-eye');
        toggleIcon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('bi-eye-slash');
        toggleIcon.classList.add('bi-eye');
    }
}

/**
 * Format a percentage value with proper coloring based on the value
 */
function formatPercentage(percentage) {
    let colorClass = 'text-success';
    
    if (percentage < 60) {
        colorClass = 'text-danger';
    } else if (percentage < 75) {
        colorClass = 'text-warning';
    }
    
    return `<span class="${colorClass}">${percentage.toFixed(1)}%</span>`;
}

/**
 * Convert a percentage to a letter grade
 */
function getLetterGrade(percentage) {
    if (percentage >= 90) {
        return 'A';
    } else if (percentage >= 80) {
        return 'B';
    } else if (percentage >= 70) {
        return 'C';
    } else if (percentage >= 60) {
        return 'D';
    } else {
        return 'F';
    }
}

/**
 * Format a grade with proper coloring and letter grade
 */
function formatGrade(percentage) {
    let colorClass = 'text-success';
    const letterGrade = getLetterGrade(percentage);
    
    if (percentage < 60) {
        colorClass = 'text-danger';
    } else if (percentage < 70) {
        colorClass = 'text-warning';
    }
    
    return `<span class="${colorClass}">${percentage.toFixed(1)}% (${letterGrade})</span>`;
}

/**
 * Update all attendance status fields in bulk
 */
function bulkUpdateAttendance(status) {
    document.querySelectorAll('select[name^="status_"]').forEach(select => {
        select.value = status;
    });
}

/**
 * Filter a table by a search term
 */
function filterTable(tableId, searchTerm) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tbody tr');
    
    searchTerm = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}
