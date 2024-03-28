$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showComments(page, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let par = $(this).parents('.commentary-options');
      $.ajax({
        method: 'DELETE',
        url: '/api/comment',
        data: {
          auth: window.localStorage.getItem('token'),
          cid: $(this).data().id
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      showHideButton($(this), '.remove-button');
    });
    $('body').on('click', '.checked-button', function() {
      $(this).blur();
      let par = $(this).parents('.commentary-options');
      $.ajax({
        method: 'PUT',
        url: '/api/comment',
        data: {
          id: $(this).data().id,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.link-button', function() {
      $(this).blur();
      window.open($(this).data().art, '_blank');
    });
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/comments/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/comments/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/comments/?page=' + p);
    });
  }
});
