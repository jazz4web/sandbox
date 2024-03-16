$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showDrafts(dt, '/api/lenta', page);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign(
          '/arts/l/' + '?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign(
        '/arts/l/' + '?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign(
        '/arts/l/' + '?page=' + p);
    });
  }
});
