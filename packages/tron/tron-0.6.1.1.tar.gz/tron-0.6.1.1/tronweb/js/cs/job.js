(function() {
  var JobListEntryView, JobRunListEntryView, JobRunListSliderModel, JobRunTimelineEntry, formatInterval, module;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  window.modules = window.modules || {};
  window.modules.job = module = {};
  window.Job = (function() {
    __extends(Job, Backbone.Model);
    function Job() {
      this.initialize = __bind(this.initialize, this);
      Job.__super__.constructor.apply(this, arguments);
    }
    Job.prototype.initialize = function(options) {
      Job.__super__.initialize.call(this, options);
      options = options || {};
      return this.refreshModel = options.refreshModel;
    };
    Job.prototype.idAttribute = "name";
    Job.prototype.urlRoot = "/jobs";
    Job.prototype.url = function() {
      return Job.__super__.url.call(this) + "?include_action_graph=1";
    };
    return Job;
  })();
  window.JobCollection = (function() {
    __extends(JobCollection, Backbone.Collection);
    function JobCollection() {
      this.comparator = __bind(this.comparator, this);
      this.parse = __bind(this.parse, this);
      this.initialize = __bind(this.initialize, this);
      JobCollection.__super__.constructor.apply(this, arguments);
    }
    JobCollection.prototype.initialize = function(models, options) {
      JobCollection.__super__.initialize.call(this, options);
      options = options || {};
      this.refreshModel = options.refreshModel;
      return this.filterModel = options.filterModel;
    };
    JobCollection.prototype.model = Job;
    JobCollection.prototype.url = "/jobs?include_job_runs=1";
    JobCollection.prototype.parse = function(resp, options) {
      return resp['jobs'];
    };
    JobCollection.prototype.comparator = function(job) {
      return job.get('name');
    };
    return JobCollection;
  })();
  window.JobRun = (function() {
    __extends(JobRun, Backbone.Model);
    function JobRun() {
      this.parse = __bind(this.parse, this);
      this.url = __bind(this.url, this);
      this.initialize = __bind(this.initialize, this);
      JobRun.__super__.constructor.apply(this, arguments);
    }
    JobRun.prototype.initialize = function(options) {
      JobRun.__super__.initialize.call(this, options);
      options = options || {};
      return this.refreshModel = options.refreshModel;
    };
    JobRun.prototype.idAttribute = "run_num";
    JobRun.prototype.urlRoot = function() {
      return "/jobs/" + this.get('name');
    };
    JobRun.prototype.url = function() {
      return JobRun.__super__.url.call(this) + "?include_action_graph=1&include_action_runs=1";
    };
    JobRun.prototype.parse = function(resp, options) {
      resp['job_url'] = "#job/" + resp['job_name'];
      return resp;
    };
    return JobRun;
  })();
  window.JobListFilterModel = (function() {
    __extends(JobListFilterModel, FilterModel);
    function JobListFilterModel() {
      JobListFilterModel.__super__.constructor.apply(this, arguments);
    }
    JobListFilterModel.prototype.filterTypes = {
      name: buildMatcher(fieldGetter('name'), matchAny),
      status: buildMatcher(fieldGetter('status'), _.str.startsWith),
      node_pool: buildMatcher(nestedName('node_pool'), _.str.startsWith)
    };
    return JobListFilterModel;
  })();
  window.JobListView = (function() {
    __extends(JobListView, Backbone.View);
    function JobListView() {
      this.renderFilter = __bind(this.renderFilter, this);
      this.renderList = __bind(this.renderList, this);
      this.initialize = __bind(this.initialize, this);
      JobListView.__super__.constructor.apply(this, arguments);
    }
    JobListView.prototype.initialize = function(options) {
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
    JobListView.prototype.tagName = "div";
    JobListView.prototype.className = "span12";
    JobListView.prototype.template = _.template("<h1>\n    <i class=\"icon-time icon-white\"></i> Scheduled Jobs\n    <span id=\"refresh\"></span>\n</h1>\n<div id=\"filter-bar\"></div>\n<div class=\"outline-block\">\n<table class=\"table table-hover table-outline table-striped\">\n    <thead class=\"header\">\n        <tr>\n            <th class=\"span4\">Name</th>\n            <th>Status</th>\n            <th>Schedule</th>\n            <th>Node Pool</th>\n            <th>Last Success</th>\n            <th>Next Run</th>\n        </tr>\n    </thead>\n    <tbody>\n    </tbody>\n</table>\n</div>");
    JobListView.prototype.render = function() {
      this.$el.html(this.template());
      this.renderFilter();
      this.$('#refresh').html(this.refreshView.render().el);
      this.renderList();
      return this;
    };
    JobListView.prototype.renderList = function() {
      var entry, model, models;
      models = this.model.filter(this.model.filterModel.createFilter());
      entry = function(model) {
        return new JobListEntryView({
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
    JobListView.prototype.renderFilter = function() {
      return this.$('#filter-bar').html(this.filterView.render().el);
    };
    return JobListView;
  })();
  JobListEntryView = (function() {
    __extends(JobListEntryView, ClickableListEntry);
    function JobListEntryView() {
      this.initialize = __bind(this.initialize, this);
      JobListEntryView.__super__.constructor.apply(this, arguments);
    }
    JobListEntryView.prototype.initialize = function(options) {
      return this.listenTo(this.model, "change", this.render);
    };
    JobListEntryView.prototype.tagName = "tr";
    JobListEntryView.prototype.className = "clickable";
    JobListEntryView.prototype.template = _.template("<td><a href=\"#job/<%= name %>\"><%= formatName(name) %></a></td>\n<td><%= formatState(status) %></td>\n<td><%= formatScheduler(scheduler) %></td>\n<td><%= displayNodePool(node_pool) %></td>\n<td><%= dateFromNow(last_success, 'never') %></td>\n<td><%= dateFromNow(next_run, 'none') %></td>");
    JobListEntryView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      makeTooltips(this.$el);
      return this;
    };
    return JobListEntryView;
  })();
  JobRunTimelineEntry = (function() {
    function JobRunTimelineEntry(jobRun, maxDate) {
      this.jobRun = jobRun;
      this.maxDate = maxDate;
      this.getEnd = __bind(this.getEnd, this);
      this.getStart = __bind(this.getStart, this);
      this.getBarClass = __bind(this.getBarClass, this);
      this.getYAxisText = __bind(this.getYAxisText, this);
      this.getYAxisLink = __bind(this.getYAxisLink, this);
      this.toString = __bind(this.toString, this);
    }
    JobRunTimelineEntry.prototype.toString = function() {
      return this.jobRun.run_num;
    };
    JobRunTimelineEntry.prototype.getYAxisLink = function() {
      return "#job/" + this.jobRun.job_name + "/" + this.jobRun.run_num;
    };
    JobRunTimelineEntry.prototype.getYAxisText = function() {
      return this.jobRun.run_num;
    };
    JobRunTimelineEntry.prototype.getBarClass = function() {
      return this.jobRun.state;
    };
    JobRunTimelineEntry.prototype.getStart = function() {
      return new Date(this.jobRun.start_time || this.jobRun.run_time);
    };
    JobRunTimelineEntry.prototype.getEnd = function() {
      if (this.jobRun.state === 'running') {
        return this.maxDate;
      }
      return new Date(this.jobRun.end_time || this.jobRun.start_time || this.jobRun.run_time);
    };
    return JobRunTimelineEntry;
  })();
  window.JobView = (function() {
    __extends(JobView, Backbone.View);
    function JobView() {
      this.formatSettings = __bind(this.formatSettings, this);
      this.renderTimeline = __bind(this.renderTimeline, this);
      this.renderGraph = __bind(this.renderGraph, this);
      this.initialize = __bind(this.initialize, this);
      JobView.__super__.constructor.apply(this, arguments);
    }
    JobView.prototype.initialize = function(options) {
      var sliderModel;
      this.listenTo(this.model, "change", this.render);
      this.refreshView = new RefreshToggleView({
        model: this.model.refreshModel
      });
      this.jobRunListView = new module.JobRunListView({
        model: this.model
      });
      this.listenTo(this.refreshView, 'refreshView', __bind(function() {
        return this.model.fetch();
      }, this));
      sliderModel = new JobRunListSliderModel(this.model);
      this.sliderView = new modules.views.SliderView({
        model: sliderModel
      });
      this.listenTo(this.sliderView, "slider:change", this.renderTimeline);
      return this.currentDate = new Date();
    };
    JobView.prototype.tagName = "div";
    JobView.prototype.className = "span12";
    JobView.prototype.template = _.template("<div class=\"row\">\n    <div class=\"span12\">\n        <h1>\n            <small>Job</small>\n            <%= formatName(name) %>\n            <span id=\"refresh\"></span>\n        </h1>\n    </div>\n    <div class=\"span5 outline-block\">\n        <h2>Details</h2>\n        <div>\n        <table class=\"table details\">\n            <tbody>\n            <tr><td>Status</td>\n                <td><%= formatState(status) %></td></tr>\n            <tr><td>Node pool</td>\n                <td><%= displayNodePool(node_pool) %></td></tr>\n            <tr><td>Schedule</td>\n                <td><%= formatScheduler(scheduler) %></td></tr>\n            <tr><td>Settings</td>\n                <td><%= settings %></td></tr>\n            <tr><td>Last success</td>\n                <td><%= dateFromNow(last_success) %></td></tr>\n            <tr><td>Next run</td>\n                <td><%= dateFromNow( next_run) %></td></tr>\n            </tbody>\n        </table>\n        </div>\n    </div>\n    <div class=\"span7 outline-block\">\n        <h2>Action Graph</h2>\n        <div id=\"action-graph\" class=\"graph job-view\"></div>\n    </div>\n\n    <div class=\"span12 outline-block\">\n      <h2>Timeline</h2>\n      <div>\n        <div id=\"slider-chart\"></div>\n        <div id=\"timeline-graph\"></div>\n      </div>\n    </div>\n\n    <div id=\"job-runs\"></div>\n</div>");
    JobView.prototype.renderGraph = function() {
      return new GraphView({
        model: this.model.get('action_graph'),
        buildContent: function(d) {
          return "<code class=\"command\">" + d.command + "</code>";
        },
        height: this.$('table.details').height() - 5
      }).render();
    };
    JobView.prototype.renderTimeline = function() {
      var jobRuns, run;
      jobRuns = this.model.get('runs').slice(0, this.sliderView.displayCount);
      jobRuns = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = jobRuns.length; _i < _len; _i++) {
          run = jobRuns[_i];
          _results.push(new JobRunTimelineEntry(run, this.currentDate));
        }
        return _results;
      }).call(this);
      return new modules.timeline.TimelineView({
        model: jobRuns
      }).render();
    };
    JobView.prototype.formatSettings = function(attrs) {
      var content, icon, template, title, _ref;
      template = _.template("<span class=\"label-icon tt-enable\" title=\"<%= title %>\">\n    <i class=\"icon-<%= icon %>\"></i>\n</span>");
      _ref = attrs.allow_overlap ? ['layers', "Allow overlapping runs"] : attrs.queueing ? ['circlepauseempty', "Queue overlapping runs"] : ['remove-circle', "Cancel overlapping runs"], icon = _ref[0], title = _ref[1];
      content = attrs.all_nodes ? template({
        icon: 'treediagram',
        title: "Run on all nodes"
      }) : "";
      return template({
        icon: icon,
        title: title
      }) + content;
    };
    JobView.prototype.render = function() {
      this.$el.html(this.template(_.extend({}, this.model.attributes, {
        settings: this.formatSettings(this.model.attributes)
      })));
      this.$('#job-runs').html(this.jobRunListView.render().el);
      this.$('#refresh').html(this.refreshView.render().el);
      this.renderGraph();
      this.renderTimeline();
      this.$('#slider-chart').html(this.sliderView.render().el);
      makeTooltips(this.$el);
      modules.views.makeHeaderToggle(this.$el);
      return this;
    };
    return JobView;
  })();
  JobRunListSliderModel = (function() {
    function JobRunListSliderModel(model) {
      this.model = model;
      this.length = __bind(this.length, this);
    }
    JobRunListSliderModel.prototype.length = function() {
      return this.model.get('runs').length;
    };
    return JobRunListSliderModel;
  })();
  module.JobRunListView = (function() {
    __extends(JobRunListView, Backbone.View);
    function JobRunListView() {
      this.render = __bind(this.render, this);
      this.renderList = __bind(this.renderList, this);
      this.initialize = __bind(this.initialize, this);
      JobRunListView.__super__.constructor.apply(this, arguments);
    }
    JobRunListView.prototype.initialize = function(options) {
      var sliderModel;
      sliderModel = new JobRunListSliderModel(this.model);
      this.sliderView = new modules.views.SliderView({
        model: sliderModel
      });
      return this.listenTo(this.sliderView, "slider:change", this.renderList);
    };
    JobRunListView.prototype.tagName = "div";
    JobRunListView.prototype.className = "span12 outline-block";
    JobRunListView.prototype.template = _.template("<h2>Job Runs</h2>\n<div>\n<div id=\"slider-table\"></div>\n<table class=\"table table-hover table-outline table-striped\">\n    <thead class=\"sub-header\">\n        <tr>\n            <th>Id</th>\n            <th>State</th>\n            <th>Node</th>\n            <th>Start</th>\n            <th>End</th>\n        </tr>\n    </thead>\n    <tbody class=\"jobruns\">\n    </tbody>\n</table>\n</div>");
    JobRunListView.prototype.renderList = function() {
      var entry, model, models;
      entry = function(jobrun) {
        return new JobRunListEntryView({
          model: new JobRun(jobrun)
        }).render().el;
      };
      models = this.model.get('runs').slice(0, this.sliderView.displayCount);
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
    JobRunListView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      this.$('#slider-table').html(this.sliderView.render().el);
      this.renderList();
      return this;
    };
    return JobRunListView;
  })();
  module.formatManualRun = function(manual) {
    if (!manual) {
      return "";
    } else {
      return "<span class=\"label label-manual\">\n    <i class=\"icon-hand-down icon-white tt-enable\" title=\"Manual run\"></i>\n</span>";
    }
  };
  formatInterval = function(interval) {
    var humanized;
    humanized = getDuration(interval).humanize();
    return "<span class=\"tt-enable\" title=\"" + interval + "\">\n " + humanized + "\n</span>";
  };
  window.formatScheduler = function(scheduler) {
    var icon, value, _ref;
    _ref = (function() {
      switch (scheduler.type) {
        case 'constant':
          return ['icon-repeatone', 'constant'];
        case 'interval':
          return ['icon-time', formatInterval(scheduler.value)];
        case 'groc':
          return ['icon-calendarthree', scheduler.value];
        case 'daily':
          return ['icon-notestasks', scheduler.value];
        case 'cron':
          return ['icon-calendaralt-cronjobs', scheduler.value];
      }
    })(), icon = _ref[0], value = _ref[1];
    return _.template("    <i class=\"<%= icon %> tt-enable\"\n        title=\"<%= type %> scheduler\"></i>\n<span class=\"scheduler label label-clear\">\n    <%= value %>\n</span>\n<% if (jitter) { %>\n    <i class=\"icon-random tt-enable\" title=\"Jitter<%= jitter %>\"></i>\n<% } %>")({
      icon: icon,
      type: scheduler.type,
      value: value,
      jitter: scheduler.jitter
    });
  };
  JobRunListEntryView = (function() {
    __extends(JobRunListEntryView, ClickableListEntry);
    function JobRunListEntryView() {
      this.initialize = __bind(this.initialize, this);
      JobRunListEntryView.__super__.constructor.apply(this, arguments);
    }
    JobRunListEntryView.prototype.initialize = function(options) {
      return this.listenTo(this.model, "change", this.render);
    };
    JobRunListEntryView.prototype.tagName = "tr";
    JobRunListEntryView.prototype.className = "clickable";
    JobRunListEntryView.prototype.template = _.template("<td>\n    <a href=\"#job/<%= job_name %>/<%= run_num %>\"><%= run_num %></a>\n    <%= modules.job.formatManualRun(manual) %>\n</td>\n<td><%= formatState(state) %></td>\n<td><%= displayNode(node) %></td>\n<td><%= dateFromNow(start_time || run_time, \"Unknown\") %></td>\n<td><%= dateFromNow(end_time, \"\") %></td>");
    JobRunListEntryView.prototype.render = function() {
      this.$el.html(this.template(this.model.attributes));
      makeTooltips(this.$el);
      return this;
    };
    return JobRunListEntryView;
  })();
  window.JobRunView = (function() {
    __extends(JobRunView, Backbone.View);
    function JobRunView() {
      this.render = __bind(this.render, this);
      this.sortActionRuns = __bind(this.sortActionRuns, this);
      this.renderGraph = __bind(this.renderGraph, this);
      this.renderTimeline = __bind(this.renderTimeline, this);
      this.getMaxDate = __bind(this.getMaxDate, this);
      this.renderList = __bind(this.renderList, this);
      this.initialize = __bind(this.initialize, this);
      JobRunView.__super__.constructor.apply(this, arguments);
    }
    JobRunView.prototype.initialize = function(options) {
      this.listenTo(this.model, "change", this.render);
      this.refreshView = new RefreshToggleView({
        model: this.model.refreshModel
      });
      return this.listenTo(this.refreshView, 'refreshView', __bind(function() {
        return this.model.fetch();
      }, this));
    };
    JobRunView.prototype.tagName = "div";
    JobRunView.prototype.className = "span12";
    JobRunView.prototype.template = _.template(" <div class=\"row\">\n    <div class=\"span12\">\n        <h1>\n            <small>Job Run</small>\n            <a href=\"<%= job_url %>\">\n                <%= formatName(job_name) %></a>.<%= run_num %>\n            <span id=\"filter\"</span>\n        </h1>\n\n    </div>\n    <div class=\"span5 outline-block\">\n        <h2>Details</h2>\n        <div>\n        <table class=\"table details\">\n            <tr><td class=\"span2\">State</td>\n                <td><%= formatState(state) %></td></tr>\n            <tr><td>Node</td>\n                <td><%= displayNode(node) %></td></tr>\n            <tr><td>Scheduled</td>\n                <td>\n                    <%= modules.job.formatManualRun(manual) %>\n                    <span class=\"label label-clear\"><%= run_time %></span>\n                </td></tr>\n            <tr><td>Start</td>\n                <td><%= dateFromNow(start_time, '') %></td>\n            </tr>\n            <tr><td>End</td>\n                <td><%= dateFromNow(end_time, '') %></td>\n            </tr>\n        </table>\n        </div>\n    </div>\n    <div class=\"span7 outline-block\">\n        <h2>Action Graph</h2>\n        <div id=\"action-graph\" class=\"graph job-view\"></div>\n    </div>\n\n    <div class=\"span12 outline-block\">\n      <h2>Timeline</h2>\n      <div>\n        <div id=\"slider-chart\"></div>\n        <div id=\"timeline-graph\"></div>\n      </div>\n    </div>\n\n    <div class=\"span12 outline-block\">\n        <h2>Action Runs</h2>\n        <div>\n        <table class=\"table table-hover table-outline\">\n            <thead class=\"sub-header\">\n                <tr>\n                    <th>Name</th>\n                    <th>State</th>\n                    <th class=\"span3\">Command</th>\n                    <th>Node</th>\n                    <th>Start</th>\n                    <th>End</th>\n                </tr>\n            </thead>\n            <tbody class=\"actionruns\">\n            </tbody>\n        </table>\n        </div>\n    </div>\n</div>");
    JobRunView.prototype.renderList = function(actionRuns) {
      var entry, model;
      entry = __bind(function(run) {
        var model;
        run['job_name'] = this.model.get('job_name');
        run['run_num'] = this.model.get('run_num');
        model = new modules.actionrun.ActionRun(run);
        return new modules.actionrun.ActionRunListEntryView({
          model: model
        }).render().el;
      }, this);
      return this.$('tbody.actionruns').html((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = actionRuns.length; _i < _len; _i++) {
          model = actionRuns[_i];
          _results.push(entry(model));
        }
        return _results;
      })());
    };
    JobRunView.prototype.getMaxDate = function() {
      var actionRuns, date, dates, r;
      actionRuns = this.model.get('runs');
      dates = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = actionRuns.length; _i < _len; _i++) {
          r = actionRuns[_i];
          _results.push(r.end_time || r.start_time);
        }
        return _results;
      })();
      dates = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = dates.length; _i < _len; _i++) {
          date = dates[_i];
          if (date != null) {
            _results.push(new Date(date));
          }
        }
        return _results;
      })();
      dates.push(new Date(this.model.get('run_time')));
      return _.max(dates);
    };
    JobRunView.prototype.renderTimeline = function(actionRuns) {
      var actionRun, maxDate;
      maxDate = this.getMaxDate();
      actionRuns = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = actionRuns.length; _i < _len; _i++) {
          actionRun = actionRuns[_i];
          _results.push(new modules.actionrun.ActionRunTimelineEntry(actionRun, maxDate));
        }
        return _results;
      })();
      return new modules.timeline.TimelineView({
        model: actionRuns,
        margins: {
          left: 150
        }
      }).render();
    };
    JobRunView.prototype.popupTemplate = _.template("<div class=\"top-right-corner\"><%= formatState(state) %></div>\n<code class=\"command\"><%= command || raw_command %></code>");
    JobRunView.prototype.renderGraph = function() {
      return new GraphView({
        model: this.model.get('action_graph'),
        buildContent: this.popupTemplate,
        nodeClass: function(d) {
          return "node " + d.state;
        },
        height: this.$('table.details').height() - 5
      }).render();
    };
    JobRunView.prototype.sortActionRuns = function() {
      var getStart, maxDate;
      maxDate = this.getMaxDate();
      getStart = function(item) {
        if (item.start_time) {
          return new Date(item.start_time);
        } else {
          return maxDate;
        }
      };
      return _.sortBy(this.model.get('runs'), getStart);
    };
    JobRunView.prototype.render = function() {
      var actionRuns;
      this.$el.html(this.template(this.model.attributes));
      this.$('#filter').html(this.refreshView.render().el);
      actionRuns = this.sortActionRuns();
      this.renderList(actionRuns);
      this.renderGraph();
      this.renderTimeline(actionRuns);
      makeTooltips(this.$el);
      modules.views.makeHeaderToggle(this.$el);
      return this;
    };
    return JobRunView;
  })();
}).call(this);
