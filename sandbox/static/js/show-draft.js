function showDraft(slug, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/draft',
    headers: tee,
    data: {
      slug: slug
    },
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.draft) {
        $('title').text($('title').text().trim() + ' ' + data.draft.title);
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftt').html(), data);
        $('#main-container').append(html);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
        let labels = $('#labels-edit').val().trim();
        if (labels.slice(-1) === ',') labels = labels.slice(0, -1);
        $('#labels-edit').val(labels);
        let lhtml = $('.labels').html().trim().slice(0, -1);
        $('.labels').html(lhtml);
        if (!data.draft.meta) {
          $('#d-length-value').text(180);
        } else {
          $('#d-length-value').text(180 - data.draft.meta.length);
        }
        if (!data.draft.summary) {
          $('#s-length-value').text(512);
        } else {
          $('#s-length-value').text(512 - data.draft.summary.length);
        }
        checkMC(860);
        // here;
      }
    },
    dataType: 'json'
  });
}
