$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showBlog(username, page, dt);
  $('body').on('click', '.page-link', {username: username}, function(event) {
    event.preventDefault();
    let th = $(this).parent();
    if (!th.hasClass('active')) {
      window.location.assign(
        '/blogs/' + event.data.username + '?page=' + $(this).text().trim());
    }
  });
  $('body')
  .on('click', '#next-link', {username: username, page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) + 1;
    window.location.assign('/blogs/' + event.data.username + '?page=' + p);
  });
  $('body').on(
    'click', '#prev-link', {username: username, page: page}, function(event) {
    event.preventDefault();
    let p = parseInt(event.data.page.trim()) - 1;
    window.location.assign('/blogs/' + event.data.username + '?page=' + p);
  });
});
