(function() {
  var ServiceInstanceView, ServiceListEntryView;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.Service = (function() {
    __extends(Service, Backbone.Model);
    function Service() {
      this.initialize = __bind(this.initialize, this);
      this.url = __bind(this.url, this);
      Service.__super__.constructor.apply(this, arguments);
    }
    Service.prototype.idAttribute = "name";
    Service.prototype.urlRoot = "/services";
    Service.prototype.url = function() {
      return "" + this.urlRoot + "/" + (this.get(this.idAttribute)) + "?include_events=6";
    };
    Service.prototype.initialize = function(options) {
      Service.__super__.initialize.call(this, options);
      options = options || {};
      return this.refreshModel = options.refreshModel;
    };
    return Service;
  })();
  window.ServiceInstance = (function() {
    __extends(ServiceInstance, Backbone.Model);
    function ServiceInstance() {
      ServiceInstance.__super__.constructor.apply(this, arguments);
    }
    return ServiceInstance;
  })();
  window.ServiceCollection = (function() {
    __extends(ServiceCollection, Backbone.Collection);
    function ServiceCollection() {
      this.comparator = __bind(this.comparator, this);
      this.parse = __bind(this.parse, this);
      this.initialize = __bind(this.initialize, this);
      ServiceCollection.__super__.constructor.apply(this, arguments);
    }
    ServiceCollection.prototype.initialize = function(models, options) {
      ServiceCollection.__super__.initialize.call(this, options);
      options = options || {};
      this.refreshModel = options.refreshModel;
      return this.filterModel = options.filterModel;
    };
    ServiceCollection.prototype.model = Service;
    ServiceCollection.prototype.url = "/services";
    ServiceCollection.prototype.parse = function(resp, options) {
      return resp['services'];
    };
    ServiceCollection.prototype.comparator = function(service) {
      return service.get('name');
    };
    return ServiceCollection;
  })();
  window.ServiceListView = (function() {
    __extends(ServiceListView, Backbone.View);
    function ServiceListView() {
      this.renderList = __bind(this.renderList, this);
      this.initialize = __bind(this.initialize, this);
      ServiceListView.__super__.constructor.apply(this, arguments);
    }
    ServiceListView.prototype.initialize = function(options) {
      this.listenTo(this.model, "sync", this.render);
      this.refreshView = new RefreshToggleView({
        model: this.model.refreshModel
      });
      this.filterView = new FilterView({
        model: this.model.filterModel
      });
      this.listenTo(this.refreshView, 'refreshView', __bind(function() {
        return this.model.fetch();
      }, this));
      return this.listenTo(this.filterView, "filter:change", this.renderList);
    };
    ServiceListView.prototype.tagName = "div";
    ServiceListView.prototype.className = "span12";
    ServiceListView.prototype.template = _.template("<h1>\n    <i class=\"icon-repeat icon-white\"></i>\n    Services\n    <span id=\"refresh\"></span>\n</h1>\n<div id=\"filter-bar\"></div>\n\n<div class=\"outline-block\">\n<table class=\"table table-hover table-outline table-striped\">\n    <thead class=\"header\">\n        <tr>\n            <th>Name</td>\n            <th>State</th>\n            <th>Count</td>\n            <th>Node Pool</td>\n        </tr>\n    </thead>\n    <tbody>\n    </tbody>\n<table>\n</div>");
    ServiceListView.prototype.render = function() {
      this.$el.html(this.template());
      this.renderFilter();
      this.renderList();
      this.renderRefresh();
      makeTooltips(this.$el);
      return this;
    };
    ServiceListView.prototype.renderList = function() {
      var entry, model, models;
      models = this.model.filter(this.model.filterModel.createFilter());
      entry = function(model) {
        return new ServiceListEntryView({
          model: model
        }).render().el;
      };
      return this.$('tbody').html((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = models.length; _i < _len; _i++) {
          model = models[_i];
          _results.push(entry(model));
        }
        return _results;
      })());
    };
    ServiceListView.prototype.renderRefresh = function() {
      return this.$('#refresh').html(this.refreshView.render().el);
    };
    ServiceListView.prototype.renderFilter = function() {
      return this.$('#filter-bar').html(this.filterView.render().el);
    };
    ServiceListView.prototype.filter = function(prefix) {
      return this.renderList(this.model.filter(function(job) {
        return _.str.startsWith(job.get('name'), prefix);
      }));
    };
    return ServiceListView;
  })();
  ServiceListEntryView = (function() {
    __extends(ServiceListEntryView, ClickableListEntry);
    function ServiceListEntryView() {
      this.initialize = __bind(this.initialize, this);
      ServiceListEntryView.__super__.constructor.apply(this, arguments);
    }
    ServiceListEntryView.prototype.initialize = function(options) {
      return this.listenTo(this.model, "change", this.render);
    };
    ServiceListEntryView.prototype.tagName = "tr";
    ServiceListEntryView.prototype.className = "clickable";
    ServiceListEntryView.prototype.template = _.template("<td><a href=\"#service/<%= name %>\"><%= formatName(name) %></a></td>\n<td><%= formatState(state) %></td>\n<td>\n    <span class=\"label label-inverse\">\n        <%= live_count %> / <%= count %></span>\n</td>\n<td><%= displayNodePool(node_pool) %></td>");
    ServiceListEntryView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      return this;
    };
    return ServiceListEntryView;
  })();
  window.ServiceView = (function() {
    __extends(ServiceView, Backbone.View);
    function ServiceView() {
      this.renderInstances = __bind(this.renderInstances, this);
      this.renderEvents = __bind(this.renderEvents, this);
      this.initialize = __bind(this.initialize, this);
      ServiceView.__super__.constructor.apply(this, arguments);
    }
    ServiceView.prototype.initialize = function(options) {
      this.listenTo(this.model, "change", this.render);
      this.refreshView = new RefreshToggleView({
        model: this.model.refreshModel
      });
      return this.listenTo(this.refreshView, 'refreshView', __bind(function() {
        return this.model.fetch();
      }, this));
    };
    ServiceView.prototype.tagName = "div";
    ServiceView.prototype.className = "span12";
    ServiceView.prototype.template = _.template("<div class=\"row\">\n    <div class=\"span12\">\n        <h1>\n            <small>Service</small>\n            <%= name %>\n            <span id=\"refresh\"></span>\n        </h1>\n    </div>\n    <div class=\"span8 outline-block\">\n        <h2>Details</h2>\n        <table class=\"table details\">\n            <tr><td class=\"span2\">Count</td>\n                <td><span class=\"label label-inverse\">\n                    <%= live_count %> / <%= count %></span>\n                </td></tr>\n            <tr><td>Node Pool</td>\n                <td><%= displayNodePool(node_pool) %></td></tr>\n            <tr><td>State</td>\n                <td><%= formatState(state) %></td></tr>\n            <tr><td>Command</td>    <td><code><%= command %></code></td></tr>\n            <tr><td>Restart Delay</td>\n                <td>\n                    <% if (restart_delay) { %>\n                        <span class=\"label label-clear\">\n                            <%= restart_delay %> seconds</span>\n                    <% } else { %>\n                        <span class=\"label info\">none</span>\n                    <% } %>\n                </td></tr>\n            <tr><td>Monitor Interval</td>\n                <td>\n                    <span class=\"label label-clear\">\n                        <%= monitor_interval %> seconds\n                    </span>\n                </td></tr>\n        </table>\n    </div>\n    <div class=\"span4 outline-block\">\n       <h2>Events</h2>\n         <table id=\"event-list\" class=\"table table-hover\">\n           <tbody>\n           </tbody>\n         </table>\n    </div>\n\n    <% if (instances.length > 0) { %>\n    <div class=\"span12 outline-block\">\n        <h2>Instances</h2>\n        <table class=\"table table-outline\">\n            <thead class=\"sub-header\">\n                <tr>\n                    <th>Id</th>\n                    <th>State</th>\n                    <th>Node</th>\n                    <th></th>\n                </tr>\n            </thead>\n            <tbody class=\"instances\">\n            </tbody>\n        </table>\n    </div>\n    <% } %>\n\n</div>");
    ServiceView.prototype.renderEvents = function(data) {
      var entry, model;
      entry = function(event) {
        return new MinimalEventListEntryView({
          model: new TronEvent(event)
        }).render().el;
      };
      return this.$('#event-list tbody').html((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          model = data[_i];
          _results.push(entry(model));
        }
        return _results;
      })());
    };
    ServiceView.prototype.renderInstances = function(data) {
      var entry, model;
      entry = function(inst) {
        return new ServiceInstanceView({
          model: new ServiceInstance(inst)
        }).render().el;
      };
      return this.$('tbody.instances').html((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          model = data[_i];
          _results.push(entry(model));
        }
        return _results;
      })());
    };
    ServiceView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      this.renderInstances(this.model.get('instances'));
      this.renderEvents(this.model.get('events'));
      this.$('#refresh').html(this.refreshView.render().el);
      makeTooltips(this.$el);
      return this;
    };
    return ServiceView;
  })();
  ServiceInstanceView = (function() {
    __extends(ServiceInstanceView, Backbone.View);
    function ServiceInstanceView() {
      ServiceInstanceView.__super__.constructor.apply(this, arguments);
    }
    ServiceInstanceView.prototype.tagName = "tr";
    ServiceInstanceView.prototype.template = _.template("<td><%= formatName(id) %></td>\n<td><%= formatState(state) %></td>\n<td><%= displayNode(node) %></td>\n<td>\n<% if (failures.length) { %>\n  <pre><%= failures %></pre>\n<% } %>\n</td>");
    ServiceInstanceView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      return this;
    };
    return ServiceInstanceView;
  })();
}).call(this);
