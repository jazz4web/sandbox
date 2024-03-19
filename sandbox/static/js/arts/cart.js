$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showArt('/api/cart', slug);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.copy-link', showCopyForm);
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '#move-screen-up', function() {
      $(this).blur();
      scrollPanel($('#navigation'));
    });
    $('body').on('click', '#censor-this', {slug: slug}, censorThis);
  }
});
