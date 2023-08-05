(function() {
  var call, module;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.modules = window.modules || {};
  module = window.modules.timeline = {};
  module.padMaxDate = function(dateRange, padding) {
    var date, delta, maxDate, minDate, _ref;
    _ref = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = dateRange.length; _i < _len; _i++) {
        date = dateRange[_i];
        _results.push(moment(date));
      }
      return _results;
    })(), minDate = _ref[0], maxDate = _ref[1];
    delta = maxDate.diff(minDate);
    maxDate.add('ms', delta * padding);
    return [minDate.toDate(), maxDate.toDate()];
  };
  call = function(field) {
    return function(item) {
      return item[field]();
    };
  };
  module.TimelineView = (function() {
    __extends(TimelineView, Backbone.View);
    function TimelineView() {
      this.render = __bind(this.render, this);
      this.buildSvgBars = __bind(this.buildSvgBars, this);
      this.buildSvgAxis = __bind(this.buildSvgAxis, this);
      this.buildSvg = __bind(this.buildSvg, this);
      this.buildAxis = __bind(this.buildAxis, this);
      this.buildY = __bind(this.buildY, this);
      this.buildX = __bind(this.buildX, this);
      this.innerWidth = __bind(this.innerWidth, this);
      this.innerHeight = __bind(this.innerHeight, this);
      this.initialize = __bind(this.initialize, this);
      TimelineView.__super__.constructor.apply(this, arguments);
    }
    TimelineView.prototype.el = "#timeline-graph";
    TimelineView.prototype.initialize = function(options) {
      var verticalMargins;
      this.margins = _.extend({
        top: 30,
        right: 40,
        bottom: 20,
        left: 60
      }, options.margins);
      verticalMargins = this.margins.top + this.margins.bottom;
      this.height = options.height || this.model.length * 30 + verticalMargins;
      this.width = options.width || this.$el.innerWidth();
      return this.minBarWidth = options.minBarWidth || 5;
    };
    TimelineView.prototype.innerHeight = function() {
      return this.height - this.margins.bottom - this.margins.top;
    };
    TimelineView.prototype.innerWidth = function() {
      return this.width - this.margins.left - this.margins.right;
    };
    TimelineView.prototype.buildX = function(data) {
      var domain;
      domain = [d3.min(data, call('getStart')), d3.max(data, call('getEnd'))];
      domain = module.padMaxDate(domain, 0.02);
      return d3.time.scale().domain(domain).rangeRound([0, this.innerWidth()]);
    };
    TimelineView.prototype.buildY = function(data) {
      return d3.scale.ordinal().domain(data).rangeBands([0, this.innerHeight()], 0.1);
    };
    TimelineView.prototype.buildAxis = function(x, y) {
      var xAxis, yAxis;
      xAxis = d3.svg.axis().scale(x).orient("top").ticks([10]).tickSize(-this.innerHeight(), 0, 0).tickPadding(5);
      yAxis = d3.svg.axis().scale(y).orient("left").tickSize(0).tickPadding(5);
      return [xAxis, yAxis];
    };
    TimelineView.prototype.buildSvg = function() {
      return d3.select(this.el).append("svg").attr({
        height: this.height,
        width: this.width,
        "class": "timeline-chart"
      }).append("g").attr({
        transform: "translate(" + this.margins.left + ", " + this.margins.top + ")"
      });
    };
    TimelineView.prototype.buildSvgAxis = function(svg, xAxis, yAxis) {
      var self;
      self = this;
      svg.append("g").attr({
        "class": "x axis"
      }).call(xAxis);
      return svg.append("g").attr({
        "class": "y axis"
      }).call(yAxis).selectAll('g').each(function(d) {
        var ele;
        ele = d3.select(this);
        ele.selectAll('text').remove();
        ele.selectAll('line').remove();
        return ele.append('a').attr({
          'xlink:href': d.getYAxisLink()
        }).append('text').attr({
          x: -5,
          y: 0,
          dy: ".32em"
        }).text(d.getYAxisText());
      });
    };
    TimelineView.prototype.buildSvgBars = function(svg, data, x, y) {
      var getWidth;
      getWidth = __bind(function(d) {
        return _.max([this.minBarWidth, x(d.getEnd()) - x(d.getStart())]);
      }, this);
      return svg.selectAll('.timeline-chart').data(data).enter().append('rect').attr({
        "class": __bind(function(d) {
          return "bar " + (d.getBarClass());
        }, this),
        x: __bind(function(d) {
          return x(d.getStart());
        }, this),
        width: getWidth,
        y: __bind(function(d) {
          return y(d);
        }, this),
        height: __bind(function(d) {
          return y.rangeBand();
        }, this)
      });
    };
    TimelineView.prototype.render = function() {
      var data, svg, x, xAxis, y, yAxis, _ref, _ref2;
      this.$el.html('');
      data = this.model;
      _ref = [this.buildX(data), this.buildY(data)], x = _ref[0], y = _ref[1];
      _ref2 = this.buildAxis(x, y), xAxis = _ref2[0], yAxis = _ref2[1];
      svg = this.buildSvg();
      this.buildSvgAxis(svg, xAxis, yAxis);
      this.buildSvgBars(svg, data, x, y);
      return this;
    };
    return TimelineView;
  })();
}).call(this);
