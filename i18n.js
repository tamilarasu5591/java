const translations = {
    "English": {
        "nav_dashboard": "Dashboard",
        "nav_disease": "Disease Detection",
        "nav_weather": "Weather",
        "nav_market": "Market",
        "nav_chat": "AI Chat",
        "nav_profile": "My Profile",
        "nav_community": "Community",
        "nav_schemes": "Schemes",
        "nav_soil": "Soil Health",
        "nav_logout": "Logout",
        "overview_title": "Dashboard Overview",
        "soil_analysis": "Soil Analysis & Advisory",
        "analyze_btn": "Analyze Soil",
        "market_alert": "Market Alert",
        "view_details": "View Details"
    },
    "Tamil": {
        "nav_dashboard": "முகப்பு",
        "nav_disease": "நோய் கண்டறிதல்",
        "nav_weather": "வானிலை",
        "nav_market": "சந்தை",
        "nav_chat": "AI உதவி",
        "nav_profile": "என் விவரம்",
        
        "nav_soil": "மண் ஆரோக்கியம்",
        "nav_logout": "வெளியேறு",
        "overview_title": "முகப்பு கண்ணோட்டம்",
        "soil_analysis": "மண் பகுப்பாய்வு & ஆலோசனை",
        "analyze_btn": "மண்ணை பகுப்பாய்வு செய்",
        "market_alert": "சந்தை அறிவிப்பு",
        "view_details": "விவரங்களை காண்க"
    },
    "Hindi": {
        "nav_dashboard": "डैशबोर्ड",
        "nav_disease": "रोग का पता लगाना",
        "nav_weather": "मौसम",
        "nav_market": "बाज़ार",
        "nav_chat": "AI चैट",
        "nav_profile": "मेरी प्रोफ़ाइल",

        "nav_soil": "मृदा स्वास्थ्य",
        "nav_logout": "लॉग आउट",
        "overview_title": "डैशबोर्ड अवलोकन",
        "soil_analysis": "मिट्टी विश्लेषण और सलाह",
        "analyze_btn": "मिट्टी का विश्लेषण करें",
        "market_alert": "बाज़ार अलर्ट",
        "view_details": "विवरण देखें"
    }
};

function getLanguage() {
    let lang = 'English';
    const langMap = {
        'en': 'English',
        'ta': 'Tamil',
        'hi': 'Hindi',
        'te': 'Telugu',
        'kn': 'Kannada'
    };

    const profileStr = localStorage.getItem('profile');
    if (profileStr) {
        try {
            const profile = JSON.parse(profileStr);
            if (profile.preferred_lang && langMap[profile.preferred_lang]) {
                lang = langMap[profile.preferred_lang];
            } else if (profile.preferred_lang && translations[profile.preferred_lang]) {
                // Fallback in case the full name was saved
                lang = profile.preferred_lang;
            }
        } catch (e) { }
    } else {
        // Fallback to checking user model if profile isn't available
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                if (user.preferred_lang && langMap[user.preferred_lang]) {
                    lang = langMap[user.preferred_lang];
                } else if (user.preferred_lang && translations[user.preferred_lang]) {
                    lang = user.preferred_lang;
                }
            } catch (e) { }
        }
    }
    return lang;
}

function t(key) {
    const lang = getLanguage();
    if (!translations[lang]) return translations['English'][key] || key;
    return translations[lang][key] || translations['English'][key] || key;
}

/**
 * Check if the given translation key exists in the local translation file
 * for the current target language.
 */
function isLocalTranslation(key) {
    const lang = getLanguage();
    return !!(translations[lang] && translations[lang][key]);
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');

        // If element has icon children, we need to preserve them. 
        // For simplicity, we just replace the text node at the end usually, but it's easier to just set innerHTML on spans.
        // Let's assume the attribute is on a <span> or we replace text content safely.

        // If it's a menu link with an icon, we can just replace the text part if we structure HTML properly.
        // For now, if innerHTML contains an <i> tag, we preserve it.
        const iconMatch = el.innerHTML.match(/<i[^>]*><\/i>/i);
        if (iconMatch) {
            el.innerHTML = iconMatch[0] + " " + t(key);
        } else {
            el.innerText = t(key);
        }
    });
}

// Ensure translations are applied as soon as the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
    const savedLang = localStorage.getItem('agri_lang') || 'en';
    const selector = document.getElementById('lang-select');
    if (selector) selector.value = savedLang;
    if (savedLang !== 'en') {
        setTimeout(() => translatePage(savedLang), 500);
    }
});

/**
 * Main translation function for dynamic content (via API)
 */
async function translatePage(lang) {
    if (!lang || lang === 'en') {
        // Restore originals
        document.querySelectorAll('[data-translate]').forEach(el => {
            if (el.dataset.original) {
                // Preserve icons if they exist
                const iconMatch = el.innerHTML.match(/<i[^>]*><\/i>/i);
                if (iconMatch) {
                    el.innerHTML = iconMatch[0] + " " + el.dataset.original;
                } else {
                    el.textContent = el.dataset.original;
                }
            }
        });
        applyTranslations(); // Also run local ones
        return;
    }

    // Apply local translations first (fast)
    applyTranslations();

    const elements = document.querySelectorAll('[data-translate]');
    const textsToTranslate = [];
    const elTargets = [];

    elements.forEach(el => {
        // Skip if already handled by local i18n
        const i18nKey = el.getAttribute('data-i18n');
        if (i18nKey && isLocalTranslation(i18nKey)) return;

        // Save original text on first pass
        if (!el.dataset.original) {
            // Get text excluding icon
            const tempEl = el.cloneNode(true);
            const icon = tempEl.querySelector('i');
            if (icon) icon.remove();
            el.dataset.original = tempEl.textContent.trim();
        }

        textsToTranslate.push(el.dataset.original);
        elTargets.push(el);
    });

    if (textsToTranslate.length === 0) return;

    // Show spinner/indicator
    const spinner = document.getElementById('translate-spinner');
    if (spinner) spinner.classList.add('active');
    const indicator = document.getElementById('translating-indicator');
    if (indicator) indicator.classList.add('active');

    try {
        const res = await authFetch(`${API_BASE}/api/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texts: textsToTranslate, lang })
        });

        if (res && res.ok) {
            const data = await res.json();
            const translated = data.translations || [];
            elTargets.forEach((el, i) => {
                if (translated[i]) {
                    const iconMatch = el.innerHTML.match(/<i[^>]*><\/i>/i);
                    if (iconMatch) {
                        el.innerHTML = iconMatch[0] + " " + translated[i];
                    } else {
                        el.textContent = translated[i];
                    }
                }
            });
        }
    } catch (e) {
        console.error('Translation failed:', e);
    } finally {
        if (spinner) spinner.classList.remove('active');
        if (indicator) indicator.classList.remove('active');
    }
}

function onLanguageChange(lang) {
    localStorage.setItem('agri_lang', lang);
    const profileStr = localStorage.getItem('profile');
    if (profileStr) {
        try {
            const profile = JSON.parse(profileStr);
            profile.preferred_lang = lang;
            localStorage.setItem('profile', JSON.stringify(profile));
        } catch (e) { }
    }
    translatePage(lang);
}
