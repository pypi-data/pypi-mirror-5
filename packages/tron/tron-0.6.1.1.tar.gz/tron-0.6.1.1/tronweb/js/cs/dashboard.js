(function() {
  var matchType;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.Dashboard = (function() {
    __extends(Dashboard, Backbone.Model);
    function Dashboard() {
      this.filter = __bind(this.filter, this);
      this.sorted = __bind(this.sorted, this);
      this.models = __bind(this.models, this);
      this.fetch = __bind(this.fetch, this);
      Dashboard.__super__.constructor.apply(this, arguments);
    }
    Dashboard.prototype.initialize = function(options) {
      options = options || {};
      this.refreshModel = new RefreshModel({
        interval: 30
      });
      this.filterModel = options.filterModel;
      this.serviceList = new ServiceCollection();
      this.jobList = new JobCollection();
      this.listenTo(this.serviceList, "sync", this.change);
      return this.listenTo(this.jobList, "sync", this.change);
    };
    Dashboard.prototype.fetch = function() {
      this.serviceList.fetch();
      return this.jobList.fetch();
    };
    Dashboard.prototype.change = function(args) {
      return this.trigger("change", args);
    };
    Dashboard.prototype.models = function() {
      return this.serviceList.models.concat(this.jobList.models);
    };
    Dashboard.prototype.sorted = function() {
      return _.sortBy(this.models(), function(item) {
        return item.get('name');
      });
    };
    Dashboard.prototype.filter = function(filter) {
      return _.filter(this.sorted(), filter);
    };
    return Dashboard;
  })();
  matchType = function(item, query) {
    switch (query) {
      case 'service':
        if (item instanceof Service) {
          return true;
        }
        break;
      case 'job':
        if (item instanceof Job) {
          return true;
        }
    }
  };
  window.DashboardFilterModel = (function() {
    __extends(DashboardFilterModel, FilterModel);
    function DashboardFilterModel() {
      DashboardFilterModel.__super__.constructor.apply(this, arguments);
    }
    DashboardFilterModel.prototype.filterTypes = {
      name: buildMatcher(fieldGetter('name'), matchAny),
      type: buildMatcher(_.identity, matchType)
    };
    return DashboardFilterModel;
  })();
  window.DashboardFilterView = (function() {
    __extends(DashboardFilterView, FilterView);
    function DashboardFilterView() {
      DashboardFilterView.__super__.constructor.apply(this, arguments);
    }
    DashboardFilterView.prototype.createtype = _.template("<div class=\"input-prepend\">\n   <i class=\"icon-markerright icon-grey\"></i>\n   <div class=\"filter-select\">\n     <select id=\"filter-<%= filterName %>\"\n          class=\"span3\"\n          data-filter-name=\"<%= filterName %>Filter\">\n      <option value=\"\">All</option>\n      <option <%= isSelected(defaultValue, 'job') %>\n          value=\"job\">Scheduled Jobs</option>\n      <option <%= isSelected(defaultValue, 'service') %>\n          value=\"service\">Services</option>\n    </select>\n  </div>\n</div>");
    return DashboardFilterView;
  })();
  window.DashboardView = (function() {
    __extends(DashboardView, Backbone.View);
    function DashboardView() {
      this.renderBoxes = __bind(this.renderBoxes, this);
      this.makeView = __bind(this.makeView, this);
      this.initialize = __bind(this.initialize, this);
      DashboardView.__super__.constructor.apply(this, arguments);
    }
    DashboardView.prototype.initialize = function(options) {
      this.refreshView = new RefreshToggleView({
        model: this.model.refreshModel
      });
      this.filterView = new DashboardFilterView({
        model: this.model.filterModel
      });
      this.listenTo(this.model, "change", this.render);
      this.listenTo(this.refreshView, 'refreshView', __bind(function() {
        return this.model.fetch();
      }, this));
      return this.listenTo(this.filterView, "filter:change", this.renderBoxes);
    };
    DashboardView.prototype.tagName = "div";
    DashboardView.prototype.className = "span12 dashboard-view";
    DashboardView.prototype.template = _.template("<h1>\n    <i class=\"icon-th icon-white\"></i>\n    <small>Tron</small>\n    <a href=\"#dashboard\">Dashboard</a>\n    <span id=\"refresh\"></span>\n</h1>\n<div id=\"filter-bar\"></div>\n<div id=\"status-boxes\">\n</div>");
    DashboardView.prototype.makeView = function(model) {
      switch (model.constructor.name) {
        case Service.name:
          return new ServiceStatusBoxView({
            model: model
          });
        case Job.name:
          return new JobStatusBoxView({
            model: model
          });
      }
    };
    DashboardView.prototype.renderRefresh = function() {
      return this.$('#refresh').html(this.refreshView.render().el);
    };
    DashboardView.prototype.renderBoxes = function() {
      var item, model, models, views;
      models = this.model.filter(this.model.filterModel.createFilter());
      views = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = models.length; _i < _len; _i++) {
          model = models[_i];
          _results.push(this.makeView(model));
        }
        return _results;
      }).call(this);
      return this.$('#status-boxes').html((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = views.length; _i < _len; _i++) {
          item = views[_i];
          _results.push(item.render().el);
        }
        return _results;
      })());
    };
    DashboardView.prototype.render = function() {
      this.$el.html(this.template());
      this.$('#filter-bar').html(this.filterView.render().el);
      this.renderBoxes();
      this.renderRefresh();
      return this;
    };
    return DashboardView;
  })();
  window.StatusBoxView = (function() {
    __extends(StatusBoxView, ClickableListEntry);
    function StatusBoxView() {
      this.render = __bind(this.render, this);
      this.className = __bind(this.className, this);
      this.initialize = __bind(this.initialize, this);
      StatusBoxView.__super__.constructor.apply(this, arguments);
    }
    StatusBoxView.prototype.initialize = function(options) {
      return this.listenTo(this.model, "change", this.render);
    };
    StatusBoxView.prototype.tagName = "div";
    StatusBoxView.prototype.className = function() {
      return "span2 clickable status-box " + (this.getState());
    };
    StatusBoxView.prototype.template = _.template("<div class=\"status-header\">\n    <a href=\"<%= url %>\">\n    <%= name %></a>\n</div>\n<span class=\"count\">\n  <i class=\"<%= icon %> icon-white\"></i><%= count %>\n</span>");
    StatusBoxView.prototype.render = function() {
      var context;
      context = _.extend({}, {
        url: this.buildUrl(),
        icon: this.icon,
        count: this.count(),
        name: formatName(this.model.attributes.name)
      });
      this.$el.html(this.template(context));
      return this;
    };
    return StatusBoxView;
  })();
  window.ServiceStatusBoxView = (function() {
    __extends(ServiceStatusBoxView, StatusBoxView);
    function ServiceStatusBoxView() {
      this.count = __bind(this.count, this);
      this.getState = __bind(this.getState, this);
      this.buildUrl = __bind(this.buildUrl, this);
      ServiceStatusBoxView.__super__.constructor.apply(this, arguments);
    }
    ServiceStatusBoxView.prototype.buildUrl = function() {
      return "#service/" + (this.model.get('name'));
    };
    ServiceStatusBoxView.prototype.icon = "icon-repeat";
    ServiceStatusBoxView.prototype.getState = function() {
      return this.model.get('state');
    };
    ServiceStatusBoxView.prototype.count = function() {
      return this.model.get('instances').length;
    };
    return ServiceStatusBoxView;
  })();
  window.JobStatusBoxView = (function() {
    __extends(JobStatusBoxView, StatusBoxView);
    function JobStatusBoxView() {
      this.count = __bind(this.count, this);
      this.getState = __bind(this.getState, this);
      this.buildUrl = __bind(this.buildUrl, this);
      JobStatusBoxView.__super__.constructor.apply(this, arguments);
    }
    JobStatusBoxView.prototype.buildUrl = function() {
      return "#job/" + (this.model.get('name'));
    };
    JobStatusBoxView.prototype.icon = "icon-time";
    JobStatusBoxView.prototype.getState = function() {
      return this.model.get('status');
    };
    JobStatusBoxView.prototype.count = function() {
      if (this.model.get('runs')) {
        return _.first(this.model.get('runs')).run_num;
      } else {
        return 0;
      }
    };
    return JobStatusBoxView;
  })();
}).call(this);
