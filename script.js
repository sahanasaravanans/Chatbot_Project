// Main script for Alumni Portal

// Set current year in footer
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('current-year')) {
        document.getElementById('current-year').textContent = new Date().getFullYear();
    }
    
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');
        flashMessages.forEach(function(message) {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        });
    }, 5000);

    // Enable all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
