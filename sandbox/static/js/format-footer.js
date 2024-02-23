function formatFooter(dt) {
  let footer = $.trim($('#footer-link').text());
  let html = footer + ', ' + dt.year + ' г.';
  $('#footer-link').html(html);
}
