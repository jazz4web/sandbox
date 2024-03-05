$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showAlbums(dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let cform = $('#create-form-block');
        let fform = $('#find-pic-block');
        if (!cform.is(':hidden')) cform.slideUp('slow');
        if (!fform.is(':hidden')) fform.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $(this).addClass('clicked-item');
//        showAlbumStat($(this).data().suffix);
      }
    });
    $('body').on('click', '#create-new', function() {
      $(this).blur();
      if (!$('#title-group').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/pictures',
          data: {
            auth: window.localStorage.getItem('token'),
            title: $('#title').val(),
            state: $('#create-form-block :checked').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.replace(data.target);
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
    $('body').on(
      'keyup blur', '#title', {min: 3, max: 100, block: '.form-group'},
      markInputError);
    $('body').on('click', '#create-new-album', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fblock = $('#find-pic-block');
      if (cform.is(':hidden')) {
        if (!fblock.is(':hidden')) fblock.slideUp('slow');
        cform.slideDown('slow', function() {
          if (!fblock.is(':hidden')) fblock.slideUp('slow');
          $('#title').focus();
          scrollPanel($('.albums-options'));
          checkMC(1152);
        });
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          showUserStat();
        }
      } else {
        cform.slideUp('slow', function() { checkMC(1152); });
      }
    });

  }
});
