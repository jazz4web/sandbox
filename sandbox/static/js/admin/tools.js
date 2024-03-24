$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showTools(dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#li-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/setcounter',
        data: {
          auth: window.localStorage.getItem('token'),
          value: $('#li-edit').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('.editor-forms-block', data);
            $('.editor-forms-block').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#ipage-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/chindex',
        data: {
          auth: window.localStorage.getItem('token'),
          value: $('#ipage-suffix').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/');
          } else {
            showError('.editor-forms-block', data);
            $('.editor-forms-block').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#robots-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/chrobots',
        data: {
          auth: window.localStorage.getItem('token'),
          value: $('#reditor').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/robots.txt');
          } else {
            showError('.editor-forms-block', data);
            $('.editor-forms-block').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#perm-submit', function() {
      $(this).blur();
      let d = new Object();
      $('#default-perms-editor .perm-checkbox').each(function() {
        d[$(this).attr('id')] = $(this).prop('checked') ? 1 : 0;
      });
      d.auth = window.localStorage.getItem('token');
      $.ajax({
        method: 'PUT',
        url: '/api/chperms',
        data: d,
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('.editor-forms-block', data);
            $('.editor-forms-block').addClass('next-block');
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#user-submit', function() {
      $(this).blur();
      let tee = {
        username: $('#username').val(),
        address: $('#address').val(),
        password: $('#password').val(),
        confirma: $('#confirmation').val(),
        auth: window.localStorage.getItem('token')
      };
      if (tee.username && tee.address && tee.password && tee.confirma) {
        $.ajax({
          method: 'POST',
          url: '/api/admin-tools',
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.assign(data.redirect);
            } else {
              showError('.editor-forms-block', data);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#edit-robots', function() {
      $(this).blur();
      let r = $('#robots-editor');
      if (r.is(':hidden')) {
        r.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        r.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-index', function() {
      $(this).blur();
      let i = $('#index-editor');
      if (i.is(':hidden')) {
        i.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        i.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-li-stat', function() {
      $(this).blur();
      let l = $('#li-editor');
      if (l.is(':hidden')) {
        l.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        l.slideDown('slow');
      }
    });
    $('body').on('click', '#create-user', function() {
      $(this).blur();
      let p = $('#new-user-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-perms', function() {
      $(this).blur();
      let p = $('#default-perms-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
  }
});
