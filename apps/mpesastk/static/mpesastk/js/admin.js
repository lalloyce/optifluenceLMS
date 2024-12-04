/**
 * MPesa STK Push admin interface JavaScript
 */

function queryStatus(checkoutRequestId, listUrl) {
    // Disable the button
    const button = event.target;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Querying...';
    
    // Send query request
    fetch('/mpesa/api/query/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `checkout_request_id=${checkoutRequestId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            alert('Status updated successfully');
            // Reload the page to show updated status
            window.location.href = listUrl;
        } else {
            alert('Error querying status: ' + data.message);
            // Re-enable the button
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-sync"></i> Query Status';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error querying status. Please try again.');
        // Re-enable the button
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-sync"></i> Query Status';
    });
}

// Helper function to get CSRF token
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

// Add custom styling for badges and buttons
document.addEventListener('DOMContentLoaded', function() {
    // Style badges
    document.querySelectorAll('.badge').forEach(badge => {
        badge.style.padding = '0.5em 0.8em';
        badge.style.fontSize = '0.8em';
        badge.style.fontWeight = 'normal';
        badge.style.borderRadius = '0.25rem';
    });
    
    // Style buttons
    document.querySelectorAll('.btn-sm').forEach(btn => {
        btn.style.marginLeft = '0.25rem';
        btn.style.marginRight = '0.25rem';
    });
});
