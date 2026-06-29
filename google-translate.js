/* ==============================================
   Google Translate Widget - AgriVistara
   Provides instant client-side translation via 
   Google Translate for all pages.
   ============================================== */

// Google Translate initialization callback
function googleTranslateInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,ta,hi,te,kn,ml,bn,mr,gu,pa,ur,fr,es,ar,zh-CN',
        layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL,
        autoDisplay: false
    }, 'google_translate_element');

    // Restore saved language preference after widget loads
    setTimeout(() => {
        const savedLang = localStorage.getItem('agri_lang') || 'en';
        if (savedLang && savedLang !== 'en') {
            setGoogleTranslateLang(savedLang);
        }

        // Watch the combo dropdown for direct user changes
        // This ensures localStorage is ALWAYS in sync with whatever language is selected
        attachComboListener();
    }, 1000);
}

// Attach a listener to the Google Translate combo so localStorage stays in sync
function attachComboListener() {
    const combo = document.querySelector('.goog-te-combo');
    if (combo) {
        combo.addEventListener('change', () => {
            const lang = combo.value;
            if (lang) {
                localStorage.setItem('agri_lang', lang);
            }
        });
    } else {
        // Widget not ready yet — retry
        setTimeout(attachComboListener, 500);
    }
}

// Programmatically change the Google Translate language
function setGoogleTranslateLang(langCode) {
    const combo = document.querySelector('.goog-te-combo');
    if (combo) {
        combo.value = langCode;
        combo.dispatchEvent(new Event('change'));
    }
}

// Called when custom language selector changes
function onLanguageChange(lang) {
    localStorage.setItem('agri_lang', lang);

    // Also update profile preference
    const profileStr = localStorage.getItem('profile');
    if (profileStr) {
        try {
            const profile = JSON.parse(profileStr);
            profile.preferred_lang = lang;
            localStorage.setItem('profile', JSON.stringify(profile));
        } catch (e) { }
    }

    // Trigger Google Translate
    setGoogleTranslateLang(lang);
}

// CSS to style/hide the default Google Translate bar and integrate nicely
(function injectGoogleTranslateCSS() {
    const style = document.createElement('style');
    style.textContent = `
        /* Hide the default Google Translate top banner (iframe) only */
        .goog-te-banner-frame {
            display: none !important;
        }
        /* Hide the top-level body > .skiptranslate div (banner container) but NOT the widget */
        body > .skiptranslate {
            display: none !important;
        }
        body { top: 0 !important; }

        /* Make sure the widget container is always visible */
        #google_translate_element {
            display: inline-block !important;
            vertical-align: middle;
        }
        #google_translate_element .skiptranslate {
            display: block !important;
        }
        #google_translate_element .goog-te-gadget {
            font-family: inherit !important;
            font-size: 0 !important;
        }
        #google_translate_element .goog-te-gadget-simple {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            font-size: 0 !important;
        }
        #google_translate_element .goog-te-combo {
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.15);
            background: rgba(15, 23, 42, 0.8);
            color: #e2e8f0;
            font-family: 'Poppins', sans-serif;
            font-size: 0.85rem;
            cursor: pointer;
            outline: none;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        #google_translate_element .goog-te-combo:hover,
        #google_translate_element .goog-te-combo:focus {
            border-color: #2ecc71;
            box-shadow: 0 0 0 2px rgba(46, 204, 113, 0.25);
        }
        #google_translate_element .goog-te-combo option {
            background: #1a1a2e;
            color: #fff;
        }

        /* Hide "Powered by Google" text */
        #google_translate_element .goog-te-gadget > span { display: none !important; }
        .goog-logo-link { display: none !important; }
        
        /* Fix body shift caused by Google Translate */
        body { top: 0px !important; }
    `;
    document.head.appendChild(style);
})();

// Inject the Google Translate script
(function loadGoogleTranslateScript() {
    const script = document.createElement('script');
    script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateInit';
    script.async = true;
    document.head.appendChild(script);
})();
