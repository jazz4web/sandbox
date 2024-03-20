$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showAnnounces(page, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.slidable', slideBlock);
    $('body').on(
      'keyup blur', '#headline',
      {min: 3, max: 50, block: '.form-headline-group'}, markInputError);
    $('body').on(
      'keyup', '#body',
      {len: 1024, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('click', '#submit', function() {
      $(this).blur();
      $('#headline').trigger('blur');
      $('#body').trigger('blur');
      let head = $('.form-headline-group');
      let body = $('.form-group');
      if (!head.hasClass('has-error') && !body.hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/announces',
          data: {
            'title': $('#headline').val(),
            'text': $('#body').val(),
            'heap': $('#heap').is(':checked') ? 1 : 0,
            'auth': window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.announce) {
              window.location.assign(data.announce);
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
