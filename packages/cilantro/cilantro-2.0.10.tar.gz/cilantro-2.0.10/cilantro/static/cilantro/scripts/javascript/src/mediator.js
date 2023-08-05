// Generated by CoffeeScript 1.6.2
var __slice = [].slice;

define(['underscore'], function(_) {
  var channels, mediator;

  channels = {};
  mediator = {
    subscribe: function(channel, _handler, once) {
      var handler, _ref;

      if ((_ref = channels[channel]) == null) {
        channels[channel] = [];
      }
      if (once) {
        handler = function() {
          mediator.unsubscribe(channel, handler, true);
          return _handler.apply(null, arguments);
        };
      } else {
        handler = _handler;
      }
      return channels[channel].push(handler);
    },
    publish: function() {
      var args, channel, handler, handlers, _i, _len;

      channel = arguments[0], args = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      if (!(handlers = channels[channel])) {
        return;
      }
      for (_i = 0, _len = handlers.length; _i < _len; _i++) {
        handler = handlers[_i];
        if (handler) {
          handler.apply(null, args);
        }
      }
      setTimeout(function() {
        return channels[channel] = _.compact(handlers);
      });
    },
    unsubscribe: function(channel, handler, defer) {
      var handlers, idx;

      if (!(handlers = channels[channel])) {
        return;
      }
      if ((idx = handlers.indexOf(handler)) >= 0) {
        if (defer) {
          return handlers[idx] = null;
        } else {
          return handlers.splice(idx, 1);
        }
      }
    }
  };
  return mediator;
});
