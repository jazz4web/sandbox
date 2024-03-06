$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showAlbum(page, suffix, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.page-link', {suffix: suffix}, function(event) {
      event.preventDefault();
      window.location.assign(
        '/pictures/' + event.data.suffix + '?page=' + $(this).text().trim());
    });
    $('body')
    .on('click', '#next-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body').on('change', '#image', {suffix: suffix}, uploadPicture);
  }
});
