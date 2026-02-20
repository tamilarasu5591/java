const CACHE_NAME = 'agrivistara-v2';
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/script.js',
    '/login.html',
    '/dashboard.html',
    '/market.html',
    '/disease.html',
    '/weather.html',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

self.addEventListener('install', (e) => {
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
        })
    );
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then((response) => response || fetch(e.request))
    );
});
