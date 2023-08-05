(function() {
  var Typeahead, module;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.modules = window.modules || {};
  module = window.modules.navbar = {};
  module.NavView = (function() {
    __extends(NavView, Backbone.View);
    function NavView() {
      this.setActive = __bind(this.setActive, this);
      this.renderTypeahead = __bind(this.renderTypeahead, this);
      this.highlighter = __bind(this.highlighter, this);
      this.source = __bind(this.source, this);
      this.updater = __bind(this.updater, this);
      this.render = __bind(this.render, this);
      NavView.__super__.constructor.apply(this, arguments);
    }
    NavView.prototype.initialize = function(options) {};
    NavView.prototype.tagName = "div";
    NavView.prototype.className = "navbar navbar-static-top";
    NavView.prototype.attributes = {
      id: "menu"
    };
    NavView.prototype.events = {
      ".search-query click": "handleClick"
    };
    NavView.prototype.handleClick = function(event) {
      return console.log(event);
    };
    NavView.prototype.template = "<div class=\"navbar-inner\">\n  <div class=\"container\">\n  <ul class=\"nav\">\n    <li class=\"brand\">tron<span>web</span></li>\n    <li><a href=\"#home\">\n      <i class=\"icon-th\"></i>Dashboard</a>\n    </li>\n    <li><a href=\"#jobs\">\n      <i class=\"icon-time\"></i>Scheduled Jobs</a>\n    </li>\n    <li><a href=\"#services\">\n      <i class=\"icon-repeat\"></i>Services</a>\n    </li>\n    <li><a href=\"#configs\">\n      <i class=\"icon-wrench\"></i>Config</a>\n    </li>\n  </ul>\n\n  <form class=\"navbar-search pull-right\">\n  </form>\n\n  </div>\n</div>";
    NavView.prototype.typeaheadTemplate = "<input type=\"text\" class=\"input-medium search-query typeahead\"\n    placeholder=\"Search\"\n    autocomplete=\"off\"\n    data-provide=\"typeahead\">\n<div class=\"icon-search\"></div>";
    NavView.prototype.render = function() {
      this.$el.html(this.template);
      this.renderTypeahead();
      return this;
    };
    NavView.prototype.updater = function(item) {
      var entry;
      entry = this.model.get(item);
      routes.navigate(entry.getUrl(), {
        trigger: true
      });
      return entry.name;
    };
    NavView.prototype.source = function(query, process) {
      var entry, _, _ref, _results;
      _ref = this.model.attributes;
      _results = [];
      for (_ in _ref) {
        entry = _ref[_];
        _results.push(entry.name);
      }
      return _results;
    };
    NavView.prototype.highlighter = function(item) {
      var entry, name, typeahead;
      typeahead = this.$('.typeahead').data().typeahead;
      name = module.typeahead_hl.call(typeahead, item);
      entry = this.model.get(item);
      return "<small>" + entry.type + "</small> " + name;
    };
    NavView.prototype.sorter = function(items) {
      var containsQuery, item, lengthSort, query, startsWithQuery, uncasedItem, _i, _len, _ref;
      _ref = [[], []], startsWithQuery = _ref[0], containsQuery = _ref[1];
      query = this.query.toLowerCase();
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        item = items[_i];
        uncasedItem = item.toLowerCase();
        if (_.str.startsWith(uncasedItem, query)) {
          startsWithQuery.push(item);
        } else if (_.str.include(uncasedItem, query)) {
          containsQuery.push(item);
        }
      }
      lengthSort = function(item) {
        return item.length;
      };
      return _.sortBy(startsWithQuery, lengthSort).concat(_.sortBy(containsQuery, lengthSort));
    };
    NavView.prototype.renderTypeahead = function() {
      this.$('.navbar-search').html(this.typeaheadTemplate);
      this.$('.typeahead').typeahead({
        source: this.source,
        updater: this.updater,
        highlighter: this.highlighter,
        sorter: this.sorter
      });
      return this;
    };
    NavView.prototype.setActive = function() {
      var params, path, _ref;
      this.$('li').removeClass('active');
      _ref = modules.routes.getLocationParams(), path = _ref[0], params = _ref[1];
      path = path.split('/')[0];
      return this.$("a[href=" + path + "]").parent('li').addClass('active');
    };
    return NavView;
  })();
  Typeahead = $.fn.typeahead.Constructor.prototype;
  Typeahead.show = function() {
    var top;
    top = this.$element.position().top + this.$element[0].offsetHeight + 1;
    this.$menu.insertAfter(this.$element).css({
      top: top
    }).show();
    this.shown = true;
    return this;
  };
  module.typeahead_hl = $.fn.typeahead.Constructor.prototype.highlighter;
}).call(this);
