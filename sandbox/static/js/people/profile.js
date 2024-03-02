$(function() {
  "use strict";
  if (!cu) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showProfile(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.slidable', slideBlock);
    $('body').on('click', '#pm-message', function() {
      $(this).blur();
      window.location.assign($(this).data().url);
    });
    $('body').on('click', '#make-friend', function() {
      $(this).blur();
      $.ajax({
        method: 'POST',
        url: '/api/rel',
        data: {
          auth: window.localStorage.getItem('token'),
          uid: $(this).data().uid
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#actions-block', data);
            $('#ealert').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#blocking-button', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/rel',
        data: {
          auth: window.localStorage.getItem('token'),
          uid: $(this).data().uid
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#actions-block', data);
            $('#ealert').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
  }
  if (cu === username) {
    $('body').on('click', '#changeava', requestAvachange);
    $('body').on('click', '#changeavaf .avatar', function() {
      window.location.reload();
    });
    $('body').on('change', '#image', changeAva);
    $('body').on('click', '#changepwd', changePWD);
    $('body').on('click', '#changepwd-submit', createNewpwd);
    $('body').on('click', '#emchange', requestEmF);
    $('body').on('click', '#chaddress-submit', requestEmCh);
    $('body').on('click', '#fix-description', function() {
      $(this).blur();
      $(this).parents('.description-block').slideUp('slow');
      let editor = $('#description-e');
      editor.slideDown('slow', function() { scrollPanel(editor); });
      $('#description-editor').focus();
    });
    $('body').on('click', '#cancel-description', function() {
      $(this).blur();
      $(this).parents('#description-e').slideUp('slow');
      let description = $('.description-block');
      description.slideDown('slow', function() { scrollPanel(description); });
    });
    $('body').on(
      'keyup', '#description-editor',
      {len: 500, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('blur', '#description-editor', function() {
      let v = $(this).val();
      let g = $(this).parents('.form-group');
      if (v.length === 0) g.addClass('has-error');
    });
    $('body').on('click', '#description-submit', function() {
      $(this).blur();
      $('#description-editor').trigger('blur');
      if (!$(this).parents('.form-group')
                  .siblings('.form-group').hasClass('has-error')) {
        $.ajax({
          method: 'PUT',
          url: '/api/profile',
          data: {
            auth: window.localStorage.getItem('token'),
            text: $('#description-editor').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('.description-block', data);
              $('#ealert').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
