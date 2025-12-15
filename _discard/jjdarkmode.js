window.document.addEventListener("DOMContentLoaded", function (event) {
  const darkModeElt = $(`<li class='nav-item'><dark-mode-toggle id='theme-toggle' class='slider' appearance='toggle' permanent='true'></dark-mode-toggle></li>`);
  $('.navbar-nav.navbar-nav-scroll.ms-auto').append(darkModeElt);
  const toggle = document.querySelector('dark-mode-toggle');
  const htmlElt = $('html');
    
  // Set or remove the `dark` class the first time.
  toggle.mode === 'dark'
    ? htmlElt.attr('data-bs-theme','dark')
    : htmlElt.attr('data-bs-theme','light')
  
  // Listen for toggle changes (which includes `prefers-color-scheme` changes)
  // and toggle the `dark` class accordingly.
  toggle.addEventListener('colorschemechange', () => {
    toggle.mode === 'dark'
    ? htmlElt.attr('data-bs-theme','dark')
    : htmlElt.attr('data-bs-theme','light')
  });
  // $('.navbar-nav.navbar-nav-scroll.me-auto').attr('id','theme-toggle');
});
