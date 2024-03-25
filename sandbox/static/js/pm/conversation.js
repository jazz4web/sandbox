$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showConversation(username, page, nopage, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign(
          '/pm/' + username + '/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/pm/' + username + '?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p;
      if (!parseInt(nopage)) {
        p = parseInt($('.pagination .active .page-link').text()) - 1;
      } else {
        p = parseInt(event.data.page.trim()) - 1;
      }
      window.location.assign('/pm/' + username + '?page=' + p);
    });
    $('body').on('click', '.new-pm-button', function() {
      $(this).blur();
      let fblock = $('#new-message');
      if (fblock.is(':hidden')) {
        fblock.slideDown('slow', function() {
          scrollPanel($('.last-pm'));
        });
      } else {
        fblock.slideUp('slow');
      }
    });
    $('body').on('click', '#cancel-edit', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '#pm-editor-submit', function() {
      $(this).blur();
      let val = $('#pm-editor-edit').val();
      let mid = $(this).data().id;
      if (val) {
        $.ajax({
          method: 'PATCH',
          url: '/api/conv',
          data: {
            text: val,
            mid: mid,
            auth: window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#edit-message', data);
              $('#ealert').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.edit-button', function() {
      $(this).blur();
      if (!$('#edit-message').length) {
        $.ajax({
          method: 'PUT',
          url: '/api/conv',
          data: {
            auth: window.localStorage.getItem('token'),
            mid: $(this).data().id
          },
          success: function(data) {
            if (data.done) {
              if (data.update) window.location.reload();
              if (data.text) {
                let dt = luxon.DateTime.now();
                let html = Mustache.render($('#editpmt').html(), data);
                $('.last-pm').after(html);
                $('#edit-message').slideDown('slow', function() {
                  scrollPanel($('#edit-message'));
                });
                if ($('.today-field').length) renderTF('.today-field', dt);
              }
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('.last-pm', data);
              $('#ealert').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let p;
      if (window.location.search) {
        p = window.location.search
          .split('page')[1].split('&')[0].slice(1)[0];
      }
      let mid = $(this).data().id;
      $.ajax({
        method: 'DELETE',
        url: '/api/conv',
        data: {
          page: p ? p : 0,
          mid: mid,
          last: $('.pm-block').length,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.replace(data.redirect);
          } else {
            let html = Mustache.render($('#ealertt').html(), data);
            $('#main-container').append(html);
            showError('.content-block', data);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      showHideButton($(this), '.remove-button');
    });
    $('body').on('click', '.reload-button', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '#pm-submit', function() {
      $(this).blur();
      let text = $('#pm-editor').val();
      if (text) {
        $.ajax({
          method: 'POST',
          url: '/api/conv',
          data: {
            recipient: username,
            auth: window.localStorage.getItem('token'),
            message: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#new-message', data);
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
