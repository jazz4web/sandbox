$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showAlbum(page, suffix, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let form = $('#create-form-block');
        if (!form.is(':hidden')) form.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $('.remove-button').each(function() { $(this).fadeOut('slow'); });
        $(this).addClass('clicked-item');
        let token = window.localStorage.getItem('token');
        let tee = token ? {'x-auth-token': token} : {};
        $.ajax({
          method: 'GET',
          url: '/api/picstat',
          headers: tee,
          data: {
            suffix: $(this).data().suffix
          },
          success: function(data) {
            if (data.picture) {
              let html = Mustache.render($('#picturet').html(), data);
              $('#right-panel').empty().append(html);
              formatDateTime($('.date-field'));
              let block_width = parseInt($('.album-statistic').width());
              let pic_width = parseInt($('.picture-body img').attr('width'));
              if (pic_width >= block_width) {
                let pic_height = parseInt($('.picture-body img')
                                          .attr('height'));
                let width = block_width - 4;
                let height = Math.round(pic_height / (pic_width / width));
                $('.picture-body img').attr({
                  "width": width, "height": height
                });
              }
              $('#copy-button').on('click', {cls: '.album-form'}, copyThis);
              $('#copy-button-b')
                .on('click', {cls: '.album-form-b'}, copyThis);
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#left-panel', data);
              $('#right-panel').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.page-link', {suffix: suffix}, function(event) {
      event.preventDefault();
      window.location.assign(
        '/pictures/' + event.data.suffix + '?page=' + $(this).text().trim());
    });
    $('body')
    .on('click', '#next-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body').on('change', '#image', {suffix: suffix}, uploadPicture);
  }
});
