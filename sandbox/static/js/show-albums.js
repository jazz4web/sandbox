function showAlbums(dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures',
    data: {
      page: page
    },
    headers: tee,
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#albumst').html(), data);
        $('#main-container').append(html);
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#right-panel').append(ust);
        checkMC(1152);
        if ($('.today-field').length) renderTF('.today-field', dt);
        formatDateTime($('.date-field'));
        let pub = $('#pub-f');
        pub.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#priv-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#priv-f');
          }
        });
        let priv = $('#priv-f');
        priv.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#pub-f');
          }
        });
        let ffo = $('#ffo-f');
        ffo.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#priv-f');
          } else {
            checkBox('#pub-f');
          }
        });
      }
    },
    dataType: 'json'
  });
}
