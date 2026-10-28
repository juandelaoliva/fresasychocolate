// Short looping clips from the shop (video.loop). They load only when they first come near the screen
// and play only while visible. Without JS or with reduced motion, the poster frame stays.
(function () {
  const videos = document.querySelectorAll('video.loop[data-src]');
  if (!videos.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const io = new IntersectionObserver((entries) => {
    for (const { target: v, isIntersecting } of entries) {
      if (isIntersecting) {
        if (!v.src) v.src = v.dataset.src;
        v.play().catch(() => {});
      } else if (!v.paused) {
        v.pause();
      }
    }
  }, { rootMargin: '200px 0px' });
  videos.forEach((v) => io.observe(v));
})();
