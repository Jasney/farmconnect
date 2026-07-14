// App JS for Farm Connect
document.addEventListener('DOMContentLoaded', function() {
  let lastScrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
  const navbar = document.querySelector('.site-nav');
  const footer = document.querySelector('.site-footer');

  // Reveal sections when they enter the viewport.
  const revealItems = document.querySelectorAll('.reveal-on-scroll');
  if ('IntersectionObserver' in window && revealItems.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    revealItems.forEach(item => observer.observe(item));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  // Loading indicators
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = form.querySelector('button[type=\"submit\"]');
      if (submitBtn) {
        submitBtn.innerHTML = '<span class="loading me-2"></span>Saving...';
        submitBtn.disabled = true;
      }
    });
  });

  // Confirm deletes
  const deleteForms = document.querySelectorAll('form[action*=\"delete\"]');
  deleteForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!confirm('Are you sure? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Image preview
  const imageInputs = document.querySelectorAll('input[type=\"file\"]');
  imageInputs.forEach(input => {
    input.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const preview = document.querySelector(`#preview-${input.id}`);
          if (preview) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
          }
        };
        reader.readAsDataURL(file);
      }
    });
  });

  // Apply data-driven widths without inline CSS.
  const progressBars = document.querySelectorAll('.js-progress-width');
  progressBars.forEach((bar) => {
    const width = Number(bar.dataset.progressWidth || 0);
    const clampedWidth = Math.max(0, Math.min(100, width));
    bar.style.width = `${clampedWidth}%`;
  });

  // Hide navbar/footer on scroll down, show them on scroll up.
  if (navbar || footer) {
    window.addEventListener('scroll', function() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

      if (scrollTop > lastScrollTop && scrollTop > 50) {
        if (navbar) {
          navbar.classList.add('site-nav-hidden');
        }
        if (footer) {
          footer.classList.add('site-footer-hidden');
        }
      } else {
        if (navbar) {
          navbar.classList.remove('site-nav-hidden');
        }
        if (footer) {
          footer.classList.remove('site-footer-hidden');
        }
      }

      if (scrollTop < 50) {
        if (navbar) {
          navbar.classList.remove('site-nav-hidden');
        }
        if (footer) {
          footer.classList.remove('site-footer-hidden');
        }
      }

      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    });
  }
});
