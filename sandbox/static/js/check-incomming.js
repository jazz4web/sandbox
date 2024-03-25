function checkIncomming() {
  $.ajax({
    method: 'POST',
    url: '/api/convs',
    data: {
      auth: window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.pm) {
        let interval = setInterval(function() {
          if ($('#main-container').length) {
            let flashed = $('.top-flashed-block');
            data = {'flashed': flashed.length};
            let html = Mustache.render($('#pmalertt').html(), data);
            if (flashed.length) {
              flashed.append(html);
            } else {
              $('#main-container').prepend(html);
            }
            clearInterval(interval);
            setTimeout(function() {
              $('.top-flashed-block').next().addClass('next-block');
            }, 100);
          }
        }, 10);
        setTimeout(function() {
          $('.top-flashed-block').next().addClass('next-block');
        }, 300);
      }
    },
    dataType: 'json'
  });
}
