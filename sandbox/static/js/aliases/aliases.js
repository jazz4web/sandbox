$(function() {
  "use strict";
  if(!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showAliases(page, dt);
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let p = page;
      if ($('.remove-button').length == 1) p = p - 1;
      let suffix = $(this).data().suffix;
      $.ajax({
        method: 'DELETE',
        url: '/api/aliases',
        data: {
          suffix: suffix,
          page: p,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.replace(data.url);
          } else {
            let html = Mustache.render($('#ealertt').html(), data);
            $('#main-container').append(html);
            if ($('#new-title').length) {
              showError('#new-title', data);
            } else {
              showError('.content-block', data);
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/aliases/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/aliases/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/aliases/?page=' + p);
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      showHideButton($(this), '.remove-button');
    });
    $('body').on('keyup', '#link', function(event) {
      if (event.which == 13) $('#link-submit').trigger('click');
    });
    $('body').on('click', '#link-submit', function() {
      $(this).blur();
      let link = $('#link').val();
      if (link.startsWith('https://') || link.startsWith('http://')) {
        $.ajax({
          method: 'POST',
          url: '/api/aliases',
          data: {
            link: link,
            auth: window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.done) {
              if (data.alias) {
                $('.found-alias').remove();
                let html = Mustache.render($('#aliast').html(), data.alias);
                $('#new-title').after(html);
                formatDateTime($('.found-alias .date-field'));
                $('#link').val('');
                let b = '#alias-' + data.alias.suffix;
                $(b).on('click', copyAlias);
              } else {
                window.location.reload();
              }
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#new-title', data);
            }
          },
          dataType: 'json'
        });
      }
    });

  }
});
