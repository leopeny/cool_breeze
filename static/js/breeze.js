var cool_breeze = (function() {
  
  var _init = function () {

    $('#why').click(function(ev) {
      $('#more_info').toggle();
      ev.preventDefault();
    });

    
  }
  
  return { 
    init: _init
  }
  
})();

cool_breeze.init();