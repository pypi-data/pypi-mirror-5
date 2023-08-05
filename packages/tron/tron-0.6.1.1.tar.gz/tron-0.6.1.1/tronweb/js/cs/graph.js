(function() {
  var GraphModalView;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.GraphView = (function() {
    __extends(GraphView, Backbone.View);
    function GraphView() {
      this.render = __bind(this.render, this);
      this.addLinks = __bind(this.addLinks, this);
      this.attachEvents = __bind(this.attachEvents, this);
      this.buildSvgNodes = __bind(this.buildSvgNodes, this);
      this.buildSvgLinks = __bind(this.buildSvgLinks, this);
      this.getLinks = __bind(this.getLinks, this);
      this.buildNodeMap = __bind(this.buildNodeMap, this);
      this.initialize = __bind(this.initialize, this);
      GraphView.__super__.constructor.apply(this, arguments);
    }
    GraphView.prototype.el = "#action-graph";
    GraphView.prototype.initialize = function(options) {
      options = options || {};
      this.height = options.height || 250;
      this.width = options.width || this.$el.width();
      this.linkDistance = options.linkDistance || 80;
      this.showZoom = options.showZoom != null ? options.showZoom : true;
      this.buildContent = options.buildContent;
      return this.nodeClass = options.nodeClass || "node";
    };
    GraphView.prototype.buildNodeMap = function(data) {
      var node, nodes, _i, _len;
      nodes = {};
      for (_i = 0, _len = data.length; _i < _len; _i++) {
        node = data[_i];
        nodes[node.name] = node;
      }
      return nodes;
    };
    GraphView.prototype.getLinks = function(data) {
      var nested, node, nodes, target;
      nodes = this.buildNodeMap(data);
      nested = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          node = data[_i];
          _results.push((function() {
            var _j, _len2, _ref, _results2;
            _ref = node.dependent;
            _results2 = [];
            for (_j = 0, _len2 = _ref.length; _j < _len2; _j++) {
              target = _ref[_j];
              _results2.push({
                source: node,
                target: nodes[target]
              });
            }
            return _results2;
          })());
        }
        return _results;
      })();
      return _.flatten(nested);
    };
    GraphView.prototype.buildSvgLinks = function(links) {
      this.svg.append("svg:defs").append("svg:marker").attr("id", "arrow").attr("viewBox", "0 0 10 10").attr("refX", 16).attr("refY", 5).attr("markerUnits", "strokeWidth").attr("markerWidth", 15).attr("markerHeight", 30).attr("orient", "auto").append("svg:path").attr("d", "M 0 2 L 10 5 L 0 8 z");
      return this.link = this.svg.selectAll(".link").data(links).enter().append("line").attr("class", "link").attr("marker-end", "url(#arrow)");
    };
    GraphView.prototype.buildSvgNodes = function(data) {
      this.node = this.svg.selectAll(".node").data(data).enter().append("svg:g").call(this.force.drag).attr({
        "class": this.nodeClass,
        'data-title': function(d) {
          return d.name;
        },
        'data-html': true,
        'data-content': this.buildContent
      });
      this.node.append("svg:circle").attr("r", 6);
      return this.node.append("svg:text").attr({
        dx: 12,
        dy: "0.25em"
      }).text(function(d) {
        return d.name;
      });
    };
    GraphView.prototype.attachEvents = function() {
      $('.node').popover({
        container: this.$el,
        placement: 'top',
        trigger: 'hover'
      });
      return this.force.on("tick", __bind(function() {
        this.link.attr("x1", function(d) {
          return d.source.x;
        }).attr("y1", function(d) {
          return d.source.y;
        }).attr("x2", function(d) {
          return d.target.x;
        }).attr("y2", function(d) {
          return d.target.y;
        });
        return this.node.attr("transform", function(d) {
          return "translate(" + d.x + ", " + d.y + ")";
        });
      }, this));
    };
    GraphView.prototype.addNodes = function(data) {
      return this.force.nodes(data);
    };
    GraphView.prototype.addLinks = function(links) {
      return this.force.links(links);
    };
    GraphView.prototype.buildForce = function(height, width) {
      return this.force = d3.layout.force().charge(-400).theta(1).linkDistance(this.linkDistance).size([width, height]);
    };
    GraphView.prototype.buildSvg = function(height, width) {
      return this.svg = d3.select(this.el).append("svg").attr({
        height: height,
        width: width
      });
    };
    GraphView.prototype.render = function() {
      var links;
      this.buildForce(this.height, this.width);
      this.buildSvg(this.height, this.width);
      this.addNodes(this.model);
      links = this.getLinks(this.model);
      this.addLinks(links);
      this.force.start();
      this.buildSvgLinks(links);
      this.buildSvgNodes(this.model);
      if (this.showZoom) {
        new GraphModalView({
          el: this.el,
          model: this.model,
          graphOptions: this
        }).render();
      }
      this.attachEvents();
      return this;
    };
    return GraphView;
  })();
  GraphModalView = (function() {
    __extends(GraphModalView, Backbone.View);
    function GraphModalView() {
      this.render = __bind(this.render, this);
      this.removeGraph = __bind(this.removeGraph, this);
      this.showModal = __bind(this.showModal, this);
      this.attachEvents = __bind(this.attachEvents, this);
      this.initialize = __bind(this.initialize, this);
      GraphModalView.__super__.constructor.apply(this, arguments);
    }
    GraphModalView.prototype.initialize = function(options) {
      options = options || {};
      return this.graphOptions = options.graphOptions;
    };
    GraphModalView.prototype.events = {
      'click #view-full-screen': 'toggleModal'
    };
    GraphModalView.prototype.toggleModal = function(event) {
      return $('.modal').modal('toggle');
    };
    GraphModalView.prototype.attachEvents = function() {
      this.$('.modal').on('show', this.showModal);
      return this.$('.modal').on('hide', this.removeGraph);
    };
    GraphModalView.prototype.template = "<div class=\"top-right-corner\">\n<button class=\"btn btn-clear tt-enable\"\n        title=\"Full view\"\n        data-placement=\"top\"\n        id=\"view-full-screen\"\n    >\n    <i class=\"icon-opennewwindow icon-white\"></i>\n</button>\n</div>\n<div class=\"modal hide fade\">\n    <div class=\"modal-header\">\n        <button class=\"btn btn-clear\"\n            data-dismiss=\"modal\"\n            aria-hidden=\"true\">\n            <i class=\"icon-circledown icon-white\"></i>\n        </button>\n        <h3>\n            <i class=\"icon-barchart icon-white\"></i>\n            Action Graph\n        </h3>\n    </div>\n    <div class=\"modal-body graph job-view\">\n    </div>\n</div>";
    GraphModalView.prototype.showModal = function(event) {
      var graph, options;
      if (event.target !== $('.modal')[0]) {
        return;
      }
      options = _.extend({}, this.graphOptions, {
        model: this.model,
        el: this.$('.modal-body.graph').html('').get(),
        height: $(window).height() - 130,
        width: $(document).width() - 150,
        linkDistance: 250,
        showZoom: false
      });
      return graph = new GraphView(options).render();
    };
    GraphModalView.prototype.removeGraph = function(event) {
      if (event.target !== $('.modal')[0]) {
        return;
      }
      return this.$('.modal-body.graph').empty();
    };
    GraphModalView.prototype.render = function() {
      this.$el.append(this.template);
      this.attachEvents();
      this.delegateEvents();
      return this;
    };
    return GraphModalView;
  })();
}).call(this);
