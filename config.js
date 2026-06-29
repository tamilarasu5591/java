
// AgriVistara Configuration
// Change API_BASE for production deployment
const API_BASE = 'http://localhost:8000';
const GOOGLE_CLIENT_ID = '492820408264-5aajkp9rkfivren4vk58p1sh7ja84gmf.apps.googleusercontent.com';

// Global Preferences Loader
(function applyGlobalPreferences() {
    try {
        const prefsStr = localStorage.getItem('agri_prefs');
        const prefs = prefsStr ? JSON.parse(prefsStr) : {};

        // Expose preferences globally
        window.AGRI_PREFS = {
            darkMode: prefs.hasOwnProperty('darkMode') ? prefs.darkMode : true,
            compactView: prefs.hasOwnProperty('compactView') ? prefs.compactView : false,
            currency: prefs.currency || 'INR',
            tempUnit: prefs.tempUnit || 'C',
            dataSaver: prefs.dataSaver || false,
            offlineMode: prefs.offlineMode || false
        };

        // Apply appearance classes immediately to prevent flicker
        if (!window.AGRI_PREFS.darkMode) {
            document.documentElement.classList.add('light-mode');
        } else {
            document.documentElement.classList.remove('light-mode');
        }

        if (window.AGRI_PREFS.compactView) {
            document.documentElement.classList.add('compact-view');
        } else {
            document.documentElement.classList.remove('compact-view');
        }
    } catch (e) {
        console.error("Error loading global preferences", e);
        window.AGRI_PREFS = { darkMode: true, compactView: false, currency: 'INR', tempUnit: 'C' };
    }
})();
