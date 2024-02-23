$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  checkMC(860);
  if ($('.today-field').length) renderTF('.today-field', dt);
});
