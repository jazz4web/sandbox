function censorThis(event) {
  $(this).blur();
  $.ajax({
    method: 'PUT',
    url: '/api/cart',
    data: {
      auth: window.localStorage.getItem('token'),
      slug: event.data.slug
    },
    success: function(data) {
      if (data.message) {
        showError('#options-block', data);
        $('#ealert').addClass('next-block');
      } else {
        if (data.redirect) window.location.assign(data.redirect);
      }
    },
    dataType: 'json'
  });
}
