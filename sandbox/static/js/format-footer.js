function formatFooter(dt) {
  let footer = $.trim($('#footer-link').text());
  let html = footer + ', ' + dt.year + ' г.' + ' ' + '&copy;';
  $('#footer-link').html(html);
}
