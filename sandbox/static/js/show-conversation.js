function showConversation(username, page, nopage, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/conv',
    headers: tee,
    data: {
      username: username,
      page: page,
      nopage: nopage
    },
    success: function(data) {
      console.log(data);
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#convt').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
        if (data.incomming) scrollPanel($('.last-pm'));
        if (!data.pagination.next && data.pagination.messages) {
          for (let i = 0; i < data.pagination.messages.length; i++) {
            let message = data.pagination.messages[i];
            if (i == data.pagination.messages.length - 1) {
              html = '<button type="button"' +
                     '        title="обновить страницу"' +
                     '        class="btn btn-sm btn-default reload-button">' +
                     '  <span class="glyphicon glyphicon-refresh"' +
                     '        aria-hidden="true"></span>' +
                     '</button>';
              $('.last-pm .pm-options').append(html);
              if (message.author_username == data.cu.username) {
                if (message.received) {
                  html = '<button type="button"' +
                         '        title="новое сообщение"' +
                         '    class="btn btn-sm btn-primary new-pm-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                } else {
                  html = '<button type="button"' +
                         '        title="редактировать"' +
                         '        data-id="' + message.id + '"' +
                         '        class="btn btn-sm btn-danger edit-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                };
              } else {
                html = '<button type="button"' +
                       '        title="ответить"' +
                       '    class="btn btn-sm btn-primary new-pm-button">' +
                  '<span class="glyphicon glyphicon-edit"' +
                  '      aria-hidden="true"></span>' +
                       '</button>';
                $('.last-pm .pm-options').prepend(html);
              }
            }
          }
        }
        checkMC(860);
      }
    },
    dataType: 'json'
  });
}
