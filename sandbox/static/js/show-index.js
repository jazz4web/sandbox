function showIndex() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/index',
    headers: tee,
    success: function(data) {
      let dt = luxon.DateTime.now();
      let content = Mustache.render($('#indext').html(), data);
      $('#main-container').append(content);
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      if ($('.today-field').length) renderTF('.today-field', dt);
    },
    dataType: 'json'
  });
}
