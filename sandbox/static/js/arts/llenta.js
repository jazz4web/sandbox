$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showLabeledDrafts('/api/llenta', page, label, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.page-link', {label: label}, function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign(
          '/arts/l/t/' + event.data.label + '/?page=' + $(this).text().trim());
      }
    });
    $('body')
    .on('click', '#next-link', {page: page, label: label}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/arts/l/t/' + event.data.label + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, label: label}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/arts/l/t/' + event.data.label + '?page=' + p);
    });
  }
});
