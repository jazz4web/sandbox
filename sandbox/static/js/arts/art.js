$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showArt('/api/art', slug, dt);
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
});
