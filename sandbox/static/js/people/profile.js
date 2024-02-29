$(function() {
  "use strict";
  if (!cu) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showProfile(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  if (cu === username) {
    $('body').on('click', '#changeava', requestAvachange);
    $('body').on('click', '#changeavaf .avatar', function() {
      window.location.reload();
    });
    $('body').on('change', '#image', changeAva);
  }
});
