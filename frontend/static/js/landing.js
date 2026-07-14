document.addEventListener('DOMContentLoaded', () => {
    const revealItems = document.querySelectorAll('.reveal-on-scroll');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target);
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -40px 0px'
        });

        revealItems.forEach((item) => observer.observe(item));
    } else {
        revealItems.forEach((item) => item.classList.add('is-visible'));
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (event) => {
            const target = anchor.getAttribute('href');
            if (!target || target.length <= 1) {
                return;
            }

            const destination = document.querySelector(target);
            if (!destination) {
                return;
            }

            event.preventDefault();
            destination.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
});
