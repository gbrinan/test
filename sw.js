// 최소 서비스워커 — 정적 에셋 캐시(오프라인 셸). API·본문은 절대 캐시하지 않음.
const CACHE = "cg-static-v1";
const PRECACHE = [
  "/assets/icons/icon-192.png",
  "/assets/icons/icon-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  // 잠금 콘텐츠·인증·결제는 캐시 금지
  if (e.request.method !== "GET" || url.pathname.startsWith("/api/") || url.origin !== location.origin) return;
  // 이미지·오디오·폰트만 cache-first, 문서는 network-first
  const isAsset = /\.(png|jpg|webp|gif|mp3|wav|woff2?)$/.test(url.pathname);
  if (isAsset) {
    e.respondWith(
      caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
        if (r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); }
        return r;
      }))
    );
  } else {
    e.respondWith(
      fetch(e.request).then(r => r).catch(() => caches.match(e.request))
    );
  }
});
