var __hasProp={}.hasOwnProperty,__extends=function(e,t){function r(){this.constructor=e}for(var n in t)__hasProp.call(t,n)&&(e[n]=t[n]);return r.prototype=t.prototype,e.prototype=new r,e.__super__=t.prototype,e};define(["environ","jquery","underscore","backbone"],function(e,t,n,r){var i,s,o,u;return i=!1,s=function(e){function t(){return u=t.__super__.constructor.apply(this,arguments),u}return __extends(t,e),t.prototype.registeredRoutes={},t.prototype.loadedRoutes=[],t.prototype.register=function(e,t,r){if(this.registeredRoutes[t]!=null)throw new Error(""+t+" view already registered");this.registeredRoutes[t]=r;if(e===!1){typeof r.load=="function"&&r.load(),typeof r.resolve=="function"&&r.resolve();return}return this.route(e,t,function(){var e,r,s,o,u,a,f,l;if(!i){i=!0,l=this.loadedRoutes;for(u=0,a=l.length;u<a;u++)f=l[u],typeof (e=this.registeredRoutes[f]).unload=="function"&&e.unload(),typeof (r=this.registeredRoutes[f]).pending=="function"&&r.pending();this.loadedRoutes=[],n.defer(function(){return i=!1})}return typeof (s=this.registeredRoutes[t]).load=="function"&&s.load(),typeof (o=this.registeredRoutes[t]).resolve=="function"&&o.resolve(),this.loadedRoutes.push(t)})},t}(r.Router),o=new s});