function getH() {
  let wh = $(window).outerHeight();
  let fh = $('#footer').outerHeight();
  let nh = $('#navigation').outerHeight() + 2;
  return wh - fh - nh;
}

function resize(wwidth, width) {
  if (wwidth > width) {
    $('#main-container').css({"width": width - 20,
                              "box-shadow": "0 0 10px gainsboro"});
  } else {
    $('#main-container').css({"width": wwidth - 20,
                              "box-shadow": "0 0 10px gainsboro"});
  }
}

function checkMC(width) {
  let wwidth = $(window).width();
  let mcon = $('#main-container');
  resize(wwidth, width);
  let height = getH();
  let mh = Math.round($('#main-container').outerHeight());
  if (height > mh) $('#main-container').css({"height": height});
  $(window).on('resize', {mh: mh}, function(event) {
    let wwidth = $(window).width();
    resize(wwidth, width);
    let height = getH();
    if (height > event.data.mh) {
      $('#main-container').css({"height": height});
    }
  });
}
