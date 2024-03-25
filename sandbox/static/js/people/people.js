$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showPeople(page, dt);
  $('body').on('click', '.page-link', function(event) {
    event.preventDefault();
    let th = $(this).parent();
    if (!th.hasClass('active')) {
      window.location.assign('/people/?page=' + $(this).text().trim());
    }
  });
  $('body').on('click', '#next-link', {page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) + 1;
    window.location.assign('/people/?page=' + p);
  });
  $('body').on('click', '#prev-link', {page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) - 1;
    window.location.assign('/people/?page=' + p);
  });
  if (window.localStorage.getItem('token')) checkIncomming();
});
