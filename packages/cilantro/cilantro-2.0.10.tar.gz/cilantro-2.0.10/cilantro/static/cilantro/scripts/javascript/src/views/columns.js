// Generated by CoffeeScript 1.6.2
var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['environ', 'mediator', 'jquery', 'underscore', 'backbone', 'serrano/channels'], function(environ, mediator, $, _, Backbone, channels) {
  var Columns, _ref;

  return Columns = (function(_super) {
    __extends(Columns, _super);

    function Columns() {
      this.remove = __bind(this.remove, this);
      this.add = __bind(this.add, this);
      this.render = __bind(this.render, this);      _ref = Columns.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    Columns.prototype.template = _.template('\
            <div id=columns-modal class="modal fade">\
                <div class=modal-header>\
                    <a class=close data-dismiss=modal>×</a>\
                    <h3>Data Columns</h3>\
                </div>\
                <div class=modal-body>\
                    <ul class="available-columns span5"></ul>\
                    <ul class="selected-columns span5"></ul>\
                </div>\
                <div class=modal-footer>\
                    <button data-save class="btn btn-primary">Save</button>\
                    <button data-close class=btn>Close</button>\
                </div>\
            </div>\
        ');

    Columns.prototype.availableItemTemplate = _.template('\
            <li data-id={{ id }}>\
                {{ name }}\
                <span class=controls>\
                    <button class="btn btn-success btn-mini">+</button>\
                </span>\
            </li>\
        ');

    Columns.prototype.selectedItemTemplate = _.template('\
            <li data-id={{ id }}>\
                {{ name }}\
                <span class=controls>\
                    <button class="btn btn-danger btn-mini">-</button>\
                </span>\
            </li>\
        ');

    Columns.prototype.events = {
      'click [data-close]': 'hide',
      'click [data-save]': 'save',
      'click .available-columns button': 'clickAdd',
      'click .selected-columns button': 'clickRemove'
    };

    Columns.prototype.deferred = {
      'add': false,
      'remove': false
    };

    Columns.prototype.initialize = function() {
      var _this = this;

      Columns.__super__.initialize.apply(this, arguments);
      this.setElement(this.template());
      this.$available = this.$('.available-columns');
      this.$selected = this.$('.selected-columns').sortable({
        cursor: 'move',
        forcePlaceholderSize: true,
        placeholder: 'placeholder'
      });
      this.$el.addClass('loading');
      this.collection.when(function() {
        _this.$el.removeClass('loading');
        _this.render();
        return _this.resolve();
      });
      return mediator.subscribe(channels.DATAVIEW_SYNCED, function(model) {
        var id, json, _i, _len, _ref1;

        if (model.isSession() && (json = model.get('json'))) {
          _ref1 = json.columns;
          for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
            id = _ref1[_i];
            _this.add(id);
          }
        }
      });
    };

    Columns.prototype.render = function() {
      var availableHtml, model, selectedHtml, _i, _len, _ref1;

      availableHtml = [];
      selectedHtml = [];
      _ref1 = this.collection.filter(function(model) {
        return model.get('formatter_name');
      });
      for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
        model = _ref1[_i];
        availableHtml.push(this.availableItemTemplate(model.attributes));
        selectedHtml.push(this.selectedItemTemplate(model.attributes));
      }
      this.$available.html(availableHtml.join(''));
      this.$selected.html(selectedHtml.join(''));
      return this;
    };

    Columns.prototype.show = function() {
      return this.$el.modal('show');
    };

    Columns.prototype.hide = function() {
      return this.$el.modal('hide');
    };

    Columns.prototype.save = function() {
      var ids;

      this.hide();
      ids = $.map(this.$selected.children(), function(elem) {
        var data;

        if ((data = $(elem).data()).selected && data.id) {
          return data.id;
        }
      });
      return mediator.publish(channels.DATAVIEW_COLUMNS, ids);
    };

    Columns.prototype.add = function(id) {
      this.$available.find("[data-id=" + id + "]").closest('li').hide();
      return this.$selected.find("[data-id=" + id + "]").appendTo(this.$selected).show().data('selected', true);
    };

    Columns.prototype.remove = function(id) {
      this.$selected.find("[data-id=" + id + "]").hide().data('selected', false);
      return this.$available.find("[data-id=" + id + "]").closest('li').show();
    };

    Columns.prototype.clickAdd = function(event) {
      event.preventDefault();
      return this.add($(event.target).closest('li').data('id'));
    };

    Columns.prototype.clickRemove = function(event) {
      event.preventDefault();
      return this.remove($(event.target).closest('li').data('id'));
    };

    return Columns;

  })(Backbone.View);
});
