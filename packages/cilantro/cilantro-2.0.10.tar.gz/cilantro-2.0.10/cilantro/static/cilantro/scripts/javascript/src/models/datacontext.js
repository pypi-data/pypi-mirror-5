// Generated by CoffeeScript 1.6.2
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'serrano'], function(_, Serrano) {
  var DataContextHistory, DataContexts, contexts, history, _ref, _ref1;

  DataContexts = (function(_super) {
    __extends(DataContexts, _super);

    function DataContexts() {
      _ref = DataContexts.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    DataContexts.prototype.url = App.urls.datacontexts;

    return DataContexts;

  })(Serrano.DataContexts);
  DataContextHistory = (function(_super) {
    __extends(DataContextHistory, _super);

    function DataContextHistory() {
      _ref1 = DataContextHistory.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    DataContextHistory.prototype.url = App.urls.datacontextHistory;

    return DataContextHistory;

  })(Serrano.DataContexts);
  contexts = new DataContexts;
  contexts.on('reset', function() {
    var defaults;

    if (!contexts.hasSession()) {
      defaults = {
        session: true
      };
      defaults.json = App.defaults.datacontext;
      return contexts.create(defaults);
    }
  });
  history = new DataContextHistory;
  contexts.fetch();
  history.fetch();
  return App.DataContext = contexts;
});
