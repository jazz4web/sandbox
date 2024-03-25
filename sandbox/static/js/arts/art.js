$(function() {
  "use strict";
  if (!cu) window.localStorage.removeItem('token');
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  showArt('/api/art', slug, dt);
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '.slidable', slideBlock);
    $('body').on('click', '#tape-out', {slug: slug}, follow);
    $('body').on('click', '#tape-in', {slug: slug}, follow);
    $('body').on('click', '#dislike-button', {slug: slug}, function(event) {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/dislike',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#option-block', data);
            $('#ealert').addClass('next-block');
          } else {
            if (data.done) {
              $('.like-block .value').text(data.likes);
              $('.dislike-block .value').text(data.dislikes);
              $('#like-button .value').text(data.likes);
              $('#dislike-button .value').text(data.dislikes);
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#like-button', {slug: slug}, function(event) {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/like',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#options-block', data);
            $('#ealert').addClass('next-block');
          } else {
            if (data.done) {
              $('.like-block .value').text(data.likes);
              $('.dislike-block .value').text(data.dislikes);
              $('#like-button .value').text(data.likes);
              $('#dislike-button .value').text(data.dislikes);
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#censor-this', {slug: slug}, censorThis);
    $('body').on('click', '#special-case', {slug: slug}, function(event) {
      $(this).blur();
      undressLinks(event.data.slug);
    });
  }
});
