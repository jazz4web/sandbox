$(function() {
  "use strict";
  if (!cu) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showProfile(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
});
