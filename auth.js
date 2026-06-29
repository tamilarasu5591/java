/**
 * AgriVistara Auth Utility
 * Handles JWT token injection into fetch requests and session management.
 */

const authFetch = async (url, options = {}) => {
    const token = localStorage.getItem('token');
    
    // Default headers
    const headers = { ...options.headers };
    
    // Only set Content-Type to JSON if it's not a FormData payload
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    } else {
        // For FormData, we must let the browser set the boundary headers automatically
        delete headers['Content-Type'];
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const mergedOptions = {
        ...options,
        headers: headers
    };

    const response = await fetch(url, mergedOptions);

    if (response.status === 401) {
        // Token expired or invalid
        console.warn("Session expired. Redirecting to login.");
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
        return null;
    }

    return response;
};

// Global check for protected pages
(function () {
    const protectedPages = ['dashboard.html', 'market.html', 'chat.html', 'weather.html', 'disease.html', 'profile.html', 'community.html', 'schemes.html', 'store.html', 'machinery.html'];
    const currentPage = window.location.pathname.split('/').pop();

    if (protectedPages.includes(currentPage)) {
        if (!localStorage.getItem('token')) {
            window.location.href = 'login.html';
        }
    }
})();
