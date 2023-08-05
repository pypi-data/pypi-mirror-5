(function() {
  var NodeInlineView, NodeModel, NodePoolInlineView, NodePoolModel;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  NodeModel = (function() {
    __extends(NodeModel, Backbone.Model);
    function NodeModel() {
      NodeModel.__super__.constructor.apply(this, arguments);
    }
    return NodeModel;
  })();
  NodePoolModel = (function() {
    __extends(NodePoolModel, Backbone.Model);
    function NodePoolModel() {
      NodePoolModel.__super__.constructor.apply(this, arguments);
    }
    return NodePoolModel;
  })();
  NodeInlineView = (function() {
    __extends(NodeInlineView, Backbone.View);
    function NodeInlineView() {
      this.render = __bind(this.render, this);
      NodeInlineView.__super__.constructor.apply(this, arguments);
    }
    NodeInlineView.prototype.tagName = "span";
    NodeInlineView.prototype.template = _.template("<span class=\"tt-enable\" title=\"<%= username %>@<%= hostname %>:<%= port %>\">\n    <%= name %>\n</span>");
    NodeInlineView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      return this;
    };
    return NodeInlineView;
  })();
  NodePoolInlineView = (function() {
    __extends(NodePoolInlineView, Backbone.View);
    function NodePoolInlineView() {
      this.render = __bind(this.render, this);
      NodePoolInlineView.__super__.constructor.apply(this, arguments);
    }
    NodePoolInlineView.prototype.tagName = "span";
    NodePoolInlineView.prototype.template = _.template("<span class=\"tt-enable\" title=\"<%= nodes.length %> node(s)\">\n    <%= name %>\n</span>");
    NodePoolInlineView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      return this;
    };
    return NodePoolInlineView;
  })();
  window.displayNode = function(node) {
    return new NodeInlineView({
      model: new NodeModel(node)
    }).render().$el.html();
  };
  window.displayNodePool = function(pool) {
    return new NodePoolInlineView({
      model: new NodePoolModel(pool)
    }).render().$el.html();
  };
}).call(this);
