$(function() {
  "use strict";
  if (cu && !window.localStorage.getItem('token')) {
    ping();
    window.location.reload();
  }
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showAthors(page, dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  $('body').on('click', '.page-link', function(event) {
    event.preventDefault();
    let th = $(this).parent();
    if (!th.hasClass('active')) {
      window.location.assign('/blogs/?page=' + $(this).text().trim());
    }
  });
  $('body').on('click', '#next-link', {page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) + 1;
    window.location.assign('/blogs/?page=' + p);
  });
  $('body').on('click', '#prev-link', {page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) - 1;
    window.location.assign('/blogs/?page=' + p);
  });
  if (window.localStorage.getItem('token')) checkIncomming();
});
