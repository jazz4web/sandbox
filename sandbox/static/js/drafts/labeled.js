$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showLabeledDrafts('/api/labels', page, label, dt);
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '.entity-alias a', function(event) {
      event.preventDefault();
    });
    $('body').on('click', '.page-link',{label: label}, function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign(
          '/drafts/t/' + event.data.label + '?page=' + $(this).text().trim());
      }
    });
    $('body')
    .on('click', '#next-link', {page: page, label: label}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/drafts/t/' + event.data.label + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, label: label}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/drafts/t/' + event.data.label + '?page=' + p);
    });
  }
});
