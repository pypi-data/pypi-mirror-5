(function() {
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.TronEvent = (function() {
    __extends(TronEvent, Backbone.Model);
    function TronEvent() {
      TronEvent.__super__.constructor.apply(this, arguments);
    }
    return TronEvent;
  })();
  window.MinimalEventListEntryView = (function() {
    __extends(MinimalEventListEntryView, Backbone.View);
    function MinimalEventListEntryView() {
      MinimalEventListEntryView.__super__.constructor.apply(this, arguments);
    }
    MinimalEventListEntryView.prototype.tagName = "tr";
    MinimalEventListEntryView.prototype.template = _.template("<td><%= dateFromNow(time) %></td>\n<td>\n  <span class=\"label <%= level %>\">\n    <%= name %>\n  </span>\n</td>");
    MinimalEventListEntryView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      makeTooltips(this.$el);
      return this;
    };
    return MinimalEventListEntryView;
  })();
}).call(this);
