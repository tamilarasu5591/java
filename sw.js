const CACHE_NAME = 'agrivistara-v12';
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/dashboard-layout.css',
    '/config.js',
    '/auth.js',
    '/i18n.js',
    '/script.js',
    '/login.html',
    '/dashboard.html',
    '/market.html',
    '/disease.html',
    '/weather.html',
    '/chat.html',
    '/support.html',
    '/profile.html',
    '/community.html',
    '/schemes.html',
    '/store.html',
    '/machinery.html',

    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

self.addEventListener('install', (e) => {
    self.skipWaiting();
    e.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(keys.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            }));
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then((response) => response || fetch(e.request))
    );
});
