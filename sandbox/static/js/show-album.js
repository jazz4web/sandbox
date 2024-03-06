function showAlbum(page, suffix, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures/' + suffix,
    data: {
      page: page
    },
    headers: tee,
    success: function(data) {
      console.log(data);
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
        let html = Mustache.render($('#albumt').html(), data);
        $('#main-container').append(html);
        let ast = Mustache.render($('#astatt').html(), data);
        $('#right-panel').append(ast);
        if ($('.today-field').length) renderTF('.today-field', dt);
        formatDateTime($('.date-field'));
        $('#progress-block').hide();
        let s = $('#select-status option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.album.state) {
            $(s[n]).attr('selected', 'selected');
          }
        }
        checkMC(1152);
      }
    },
    dataType: 'json'
  });
}
