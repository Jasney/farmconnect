function openVideo() {
    alert('Demo video modal can be implemented here.');
}

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.trust-section, .stats-section, .video-section, .services-section, .faq-section, .testimonials-section, .cta-last').forEach(el => observer.observe(el));

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = this.getAttribute('href');
        if (target.length > 1) {
            e.preventDefault();
            document.querySelector(target)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
