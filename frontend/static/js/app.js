// App JS for Farm Connect
document.addEventListener('DOMContentLoaded', function() {
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
});
