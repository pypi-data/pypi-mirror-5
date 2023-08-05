// Generated by CoffeeScript 1.6.2
define(['jquery', 'backbone'], function($, Backbone) {
  return $(window).on('beforeunload', function() {
    if (Backbone.ajax.pending) {
      if (App.stats.ajaxAttempts === App.ajax.maxAttempts) {
        return "Unfortunately, your data hasn't been saved. The server                    or your Internet connection is acting up. Sorry!";
      }
      return "Wow, you're quick! Your stuff is being saved.                It will only take a moment.";
    }
  });
});
