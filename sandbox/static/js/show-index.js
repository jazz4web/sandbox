function showIndex(dt) {
  $.ajax({
    method: 'GET',
    url: '/api/index',
    success: function(data) {
      let content = Mustache.render($('#indext').html(), data);
      $('#main-container').append(content);
      checkMC(860);
      if ($('.today-field').length) renderTF('.today-field', dt);
    },
    dataType: 'json'
  });
}
