var __hasProp={}.hasOwnProperty,__extends=function(e,t){function r(){this.constructor=e}for(var n in t)__hasProp.call(t,n)&&(e[n]=t[n]);return r.prototype=t.prototype,e.prototype=new r,e.__super__=t.prototype,e};define(["backbone"],function(e){var t,n,r,i;return t=function(e){function t(){return r=t.__super__.constructor.apply(this,arguments),r}return __extends(t,e),t}(e.Model),n=function(e){function n(){return i=n.__super__.constructor.apply(this,arguments),i}return __extends(n,e),n.prototype.model=t,n}(e.Collection),{DataConcept:t,DataConcepts:n}});