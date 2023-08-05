// Generated by CoffeeScript 1.6.2
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['environ', 'serrano'], function(environ, Serrano) {
  var DataConcepts, _ref;

  DataConcepts = (function(_super) {
    __extends(DataConcepts, _super);

    function DataConcepts() {
      _ref = DataConcepts.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    DataConcepts.prototype.url = App.urls.dataconcepts;

    DataConcepts.prototype.initialize = function() {
      DataConcepts.__super__.initialize.apply(this, arguments);
      this.on('reset', this.resolve);
      return this.fetch();
    };

    return DataConcepts;

  })(Serrano.DataConcepts);
  return App.DataConcept = new DataConcepts;
});
