$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  checkMC(860);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.copy-link').on('click', showCopyForm);
  $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImage);
  $('.entity-text-block img').on('click', clickImage);
});
