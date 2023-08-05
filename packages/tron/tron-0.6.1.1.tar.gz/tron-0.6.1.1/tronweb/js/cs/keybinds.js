(function() {
  var isInputField, module, setFocusBinds;
  window.modules = window.modules || {};
  module = window.modules.keybinds = {};
  isInputField = function(event) {
    var _ref;
    return (_ref = event.target.tagName.toLowerCase()) === 'input' || _ref === 'textarea';
  };
  setFocusBinds = function(el) {
    return el.bind('keydown', function(event) {
      if (isInputField(event)) {
        return;
      }
      switch (event.keyCode) {
        case 70:
          $('#view-full-screen').click();
          break;
        case 82:
          $('.refresh-view .btn').click();
          break;
        case 83:
          $('.search-query').focus();
          break;
        default:
          return;
      }
      return event.preventDefault();
    });
  };
  $(document).ready(function() {
    return setFocusBinds($(document));
  });
}).call(this);
