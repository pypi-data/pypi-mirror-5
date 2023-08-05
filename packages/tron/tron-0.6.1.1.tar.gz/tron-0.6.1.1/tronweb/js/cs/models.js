(function() {
  var CommandIndexEntry, ConfigIndexEntry, IndexEntry, JobIndexEntry, ServiceIndexEntry, backboneSync, module;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __slice = Array.prototype.slice;
  window.modules = window.modules || {};
  module = window.modules.models = {};
  backboneSync = Backbone.sync;
  Backbone.sync = function(method, model, options) {
    options.url = '/api' + _.result(model, 'url');
    return backboneSync(method, model, options);
  };
  window.RefreshModel = (function() {
    __extends(RefreshModel, Backbone.Model);
    function RefreshModel() {
      this.scheduleRefresh = __bind(this.scheduleRefresh, this);
      this.doRefresh = __bind(this.doRefresh, this);
      this.clear = __bind(this.clear, this);
      this.disableRefresh = __bind(this.disableRefresh, this);
      this.enableRefresh = __bind(this.enableRefresh, this);
      this.toggle = __bind(this.toggle, this);
      this.initialize = __bind(this.initialize, this);
      RefreshModel.__super__.constructor.apply(this, arguments);
    }
    RefreshModel.prototype.initialize = function(options) {
      options = options || {};
      this.interval = (options.interval || 5) * 1000;
      this.enabled = false;
      return this.timeout = null;
    };
    RefreshModel.prototype.toggle = function(event) {
      if (!this.enabled) {
        this.enableRefresh();
        return this.trigger('toggle:on');
      } else {
        this.disableRefresh();
        return this.trigger('toggle:off');
      }
    };
    RefreshModel.prototype.enableRefresh = function() {
      if (!this.enabled) {
        console.log("Enabling refresh");
        this.enabled = true;
        return this.scheduleRefresh();
      }
    };
    RefreshModel.prototype.disableRefresh = function() {
      console.log("Disableing refresh ");
      this.enabled = false;
      return this.clear();
    };
    RefreshModel.prototype.clear = function() {
      clearTimeout(this.timeout);
      return this.timeout = null;
    };
    RefreshModel.prototype.doRefresh = function() {
      this.clear();
      if (this.enabled) {
        console.log("trigger refresh event");
        this.trigger('refresh');
        return this.scheduleRefresh();
      }
    };
    RefreshModel.prototype.scheduleRefresh = function() {
      if (!this.timeout) {
        console.log("scheduled with " + this.interval);
        return this.timeout = setTimeout(this.doRefresh, this.interval);
      }
    };
    return RefreshModel;
  })();
  window.matchAny = function(item, query) {
    return ~item.toLowerCase().indexOf(query.toLowerCase());
  };
  window.buildMatcher = function(getter, matcher) {
    return function(item, query) {
      return matcher(getter(item), query);
    };
  };
  window.fieldGetter = function(name) {
    return function(item) {
      return item.get(name);
    };
  };
  window.nestedName = function(field) {
    return function(item) {
      return item.get(field)['name'];
    };
  };
  window.FilterModel = (function() {
    __extends(FilterModel, Backbone.Model);
    function FilterModel() {
      this.createFilter = __bind(this.createFilter, this);
      FilterModel.__super__.constructor.apply(this, arguments);
    }
    FilterModel.prototype.filterTypes = {
      name: buildMatcher(fieldGetter('name'), matchAny),
      state: buildMatcher(fieldGetter('state'), _.str.startsWith),
      node_pool: buildMatcher(nestedName('node_pool'), _.str.startsWith)
    };
    FilterModel.prototype.createFilter = function() {
      var filterFuncs, func, type;
      filterFuncs = (function() {
        var _ref, _results;
        _ref = this.filterTypes;
        _results = [];
        for (type in _ref) {
          func = _ref[type];
          _results.push(__bind(function(type, func) {
            var query;
            query = this.get("" + type + "Filter");
            if (query) {
              return function(item) {
                return func(item, query);
              };
            } else {
              return function(item) {
                return true;
              };
            }
          }, this)(type, func));
        }
        return _results;
      }).call(this);
      return function(item) {
        return _.every(filterFuncs, function(func) {
          return func(item);
        });
      };
    };
    return FilterModel;
  })();
  IndexEntry = (function() {
    function IndexEntry(name) {
      this.name = name;
      this.toString = __bind(this.toString, this);
      this.indexOf = __bind(this.indexOf, this);
      this.replace = __bind(this.replace, this);
      this.toLowerCase = __bind(this.toLowerCase, this);
    }
    IndexEntry.prototype.toLowerCase = function() {
      return this.name.toLowerCase();
    };
    IndexEntry.prototype.replace = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.name).replace.apply(_ref, args);
    };
    IndexEntry.prototype.indexOf = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.name).indexOf.apply(_ref, args);
    };
    IndexEntry.prototype.toString = function() {
      return "" + this.type + " " + this.name;
    };
    return IndexEntry;
  })();
  JobIndexEntry = (function() {
    __extends(JobIndexEntry, IndexEntry);
    function JobIndexEntry() {
      this.getUrl = __bind(this.getUrl, this);
      JobIndexEntry.__super__.constructor.apply(this, arguments);
    }
    JobIndexEntry.prototype.type = "Job";
    JobIndexEntry.prototype.getUrl = function() {
      return "#job/" + this.name;
    };
    return JobIndexEntry;
  })();
  ServiceIndexEntry = (function() {
    __extends(ServiceIndexEntry, IndexEntry);
    function ServiceIndexEntry() {
      this.getUrl = __bind(this.getUrl, this);
      ServiceIndexEntry.__super__.constructor.apply(this, arguments);
    }
    ServiceIndexEntry.prototype.type = "Service";
    ServiceIndexEntry.prototype.getUrl = function() {
      return "#service/" + this.name;
    };
    return ServiceIndexEntry;
  })();
  ConfigIndexEntry = (function() {
    __extends(ConfigIndexEntry, IndexEntry);
    function ConfigIndexEntry() {
      this.getUrl = __bind(this.getUrl, this);
      ConfigIndexEntry.__super__.constructor.apply(this, arguments);
    }
    ConfigIndexEntry.prototype.type = "Config";
    ConfigIndexEntry.prototype.getUrl = function() {
      return "#config/" + this.name;
    };
    return ConfigIndexEntry;
  })();
  CommandIndexEntry = (function() {
    __extends(CommandIndexEntry, IndexEntry);
    function CommandIndexEntry(name, job_name, action_name) {
      this.name = name;
      this.job_name = job_name;
      this.action_name = action_name;
      this.getUrl = __bind(this.getUrl, this);
    }
    CommandIndexEntry.prototype.type = "command";
    CommandIndexEntry.prototype.getUrl = function() {
      return "#job/" + this.job_name + "/-1/" + this.action_name;
    };
    return CommandIndexEntry;
  })();
  module.QuickFindModel = (function() {
    __extends(QuickFindModel, Backbone.Model);
    function QuickFindModel() {
      this.parse = __bind(this.parse, this);
      this.getJobEntries = __bind(this.getJobEntries, this);
      QuickFindModel.__super__.constructor.apply(this, arguments);
    }
    QuickFindModel.prototype.url = "/";
    QuickFindModel.prototype.getJobEntries = function(jobs) {
      var actions, buildActions, name, nested;
      buildActions = function(actions) {
        var action, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = actions.length; _i < _len; _i++) {
          action = actions[_i];
          _results.push(new CommandIndexEntry(action.command, name, action.name));
        }
        return _results;
      };
      nested = (function() {
        var _results;
        _results = [];
        for (name in jobs) {
          actions = jobs[name];
          _results.push([new JobIndexEntry(name), buildActions(actions)]);
        }
        return _results;
      })();
      return _.flatten(nested);
    };
    QuickFindModel.prototype.parse = function(resp, options) {
      var entry, index, name;
      index = [].concat(this.getJobEntries(resp['jobs']), (function() {
        var _i, _len, _ref, _results;
        _ref = resp['services'];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          name = _ref[_i];
          _results.push(new ServiceIndexEntry(name));
        }
        return _results;
      })(), (function() {
        var _i, _len, _ref, _results;
        _ref = resp['namespaces'];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          name = _ref[_i];
          _results.push(new ConfigIndexEntry(name));
        }
        return _results;
      })());
      return _.mash((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = index.length; _i < _len; _i++) {
          entry = index[_i];
          _results.push([entry.name, entry]);
        }
        return _results;
      })());
    };
    return QuickFindModel;
  })();
}).call(this);
