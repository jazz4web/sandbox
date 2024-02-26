function getheight() {
  let wh = $(window).height();
  let mnav = parseInt($('#navigation').css('marginTop').replace('px', ''));
  let nh = $('#navigation').outerHeight();
  let fh = $('#footer').outerHeight();
  let mch = Math.round($('#main-container').outerHeight());
  let clearance = wh - mnav - nh - fh - mch;
  if (clearance > 0) {
    $('#main-container').css({"margin-top": "4px"});
  } else {
    $('#main-container').css({"margin-top": 0});
  }
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
  getheight();
  $(window).on('resize', function() {
    let wwidth = $(window).width();
    resize(wwidth, width);
    getheight();
  });
}
