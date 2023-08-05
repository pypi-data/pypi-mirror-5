// Generated by CoffeeScript 1.6.2
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['environ', 'jquery', 'underscore', 'backbone'], function(environ, $, _, Backbone) {
  var CompositeArea, _ref;

  return CompositeArea = (function(_super) {
    __extends(CompositeArea, _super);

    function CompositeArea() {
      _ref = CompositeArea.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    CompositeArea.prototype.id = 'composite-area';

    CompositeArea.prototype.load = function() {
      return this.$el.fadeIn();
    };

    CompositeArea.prototype.unload = function() {
      return this.$el.hide();
    };

    return CompositeArea;

  })(Backbone.View);
});
