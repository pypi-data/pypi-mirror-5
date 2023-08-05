var __bind=function(e,t){return function(){return e.apply(t,arguments)}},__hasProp={}.hasOwnProperty,__extends=function(e,t){function r(){this.constructor=e}for(var n in t)__hasProp.call(t,n)&&(e[n]=t[n]);return r.prototype=t.prototype,e.prototype=new r,e.__super__=t.prototype,e};define(["environ","mediator","jquery","underscore","backbone","serrano","charts","forms/controls"],function(e,t,n,r,i,s,o,u){var a,f,l,c,h,p,d,v,m,g,y,b;return f=function(e){function a(){return this.update=__bind(this.update,this),this.hide=__bind(this.hide,this),this.show=__bind(this.show,this),d=a.__super__.constructor.apply(this,arguments),d}return __extends(a,e),a.prototype.template=r.template('            <div class="area-container queryview">                <h3 class=heading>                    {{ name }} <small>{{ category }}</small>                </h3>                <div class=btn-toolbar>                    <button data-toggle=detail class="btn btn-small"><i class=icon-info-sign></i> Info</button>                    <button data-toggle=hide class="btn btn-small"><i class=icon-minus></i> Hide</button>                </div>                <div class=details>                    <div class=description>{{ description }}</div>                </div>                <form class=form-inline>                </form>            </div>        '),a.prototype.events={"click [data-toggle=hide]":"toggleHide","click [data-toggle=detail]":"toggleDetail","submit form,button,input,select":"preventDefault"},a.prototype.deferred={update:!0},a.prototype.initialize=function(){var e,n,r=this;return a.__super__.initialize.apply(this,arguments),e={name:this.model.get("name"),category:(n=this.model.get("category"))?n.name:"",description:this.model.get("description")},this.setElement(this.template(e)),this.$form=this.$("form"),this.$heading=this.$(".heading"),this.$details=this.$(".details"),t.subscribe("queryview/show",function(e){if(r.model.id===e)return r.show()}),t.subscribe("queryview/hide",function(e){if(r.model.id===e)return r.hide()}),this.render()},a.prototype.preventDefault=function(e){return e.preventDefault()},a.prototype.toggleDetail=function(){return this.$details.is(":visible")?this.$details.slideUp(300):this.$details.slideDown(300)},a.prototype.toggleHide=function(e){return e.preventDefault(),t.publish("queryview/hide",this.model.id)},a.prototype.render=function(){var e,r,a,f,l,c,h,p,d,v,m,g=this;c=new i.Collection(this.model.get("fields")),this.controls=[],this.charts=[],p={label:c.length===1?!1:!0},m=c.models;for(d=0,v=m.length;d<v;d++)h=m[d],p.model=h,e=n("<div></div>"),r=h.attributes,r.simple_type==="boolean"?l=u.BooleanControl:r.enumerable?l=u.EnumerableControl:r.searchable?l=u.SearchableControl:r.simple_type==="number"?l=u.NumberControl:l=u.Control,h.get("_links").distribution?a=new o.DistributionChart({editable:!1,data:{context:null}}):a=null,this.controls.push(f=new l(p)),this.charts.push([h,a]),e.append(f.render()),this.$form.append(e),a&&this.$form.append(a.render());return t.subscribe(s.DATACONTEXT_SYNCED,function(e){var t,n,r,i,s;if(e.isSession()){i=g.controls,s=[];for(n=0,r=i.length;n<r;n++)f=i[n],(t=e.getNodes(f.model.id))&&t[0]?s.push(f.set(t[0])):s.push(void 0);return s}}),this.update(),this.$el},a.prototype.show=function(){var e,t,r,i,s;this.resolve(),e=n("#discover-area"),this.$el.prependTo(e),s=this.controls;for(r=0,i=s.length;r<i;r++)t=s[r],t.show();return this},a.prototype.hide=function(){var e,t,n=this;return t={top:"auto",left:"auto",zIndex:"auto",position:this.$el.css("position")},e=this.$el.offset(),this.$el.css({top:e.top,left:e.left,position:"fixed",zIndex:-1}),this.$el.animate({top:-this.$el.height()},{duration:600,easing:"easeOutQuad",complete:function(){return n.$el.detach().css(t)}}),this.pending(),this},a.prototype.update=function(){var e,t,n,r,i,s,o;s=this.charts;for(r=0,i=s.length;r<i;r++)o=s[r],t=o[0],e=o[1],e&&(n=t.get("_links").distribution.href,e.update(n,null,[t]))},a}(i.View),a=function(e){function n(){return v=n.__super__.constructor.apply(this,arguments),v}return __extends(n,e),n.prototype.tagName="li",n.prototype.events={"click a":"click"},n.prototype.initialize=function(){var e=this;return t.subscribe("queryview/show",function(t){return t===e.model.id?e.$el.addClass("active"):e.$el.removeClass("active")}),t.subscribe("queryview/hide",function(t){if(t===e.model.id)return e.$el.removeClass("active")})},n.prototype.render=function(){return this.model.get("published")||this.$el.addClass("staff-only").attr("data-placement","right"),this.$el.html("<a href=#>"+this.model.get("name")+"</a>")},n.prototype.click=function(e){return e.preventDefault(),t.publish("queryview/show",this.model.id)},n}(i.View),c=function(e){function t(){return m=t.__super__.constructor.apply(this,arguments),m}return __extends(t,e),t.prototype.id="data-filters-accordian",t.prototype.className="accordian",t.prototype.events={"click .accordian-toggle":"toggleCaret"},t.prototype.groupTemplate=r.template('            <div class=accordian-group>                <div class=accordian-heading>                    <a class=accordian-toggle data-toggle=collapse href="#category-{{ id }}">{{ name }}</a>                    <b class="caret closed"></b>                </div>                <div id="category-{{ id }}" class="accordian-body collapse">                    <ul class="nav nav-list"></ul>                </div>            </div>         '),t.prototype.initialize=function(){var e=this;return this.$el.addClass("loading"),this.collection.when(function(){return e.$el.removeClass("loading"),e.render(),e.collection.each(function(e,t){if(e.get("queryview"))return new f({model:e})})})},t.prototype.render=function(){var e,t,i,s,o,u,f,l,c,h,p,d,v,m,g,y,b,w,E,S,x,T,N;v={categories:[]},N=this.collection.models;for(g=0,E=N.length;g<E;g++){f=N[g];if(!f.get("queryview"))continue;i=f.attributes,s=null,h={id:null},i.category&&(i.category.parent?(s=i.category.parent,h=i.category):s=i.category),(d=v[s.id])||(v.categories.push(s),d=v[s.id]={categories:[]}),(l=d[h.id])||(h.id&&d.categories.push(h),l=d[h.id]=[]),l.push(f)}o=r.sortBy(v.categories,"order"),v[null]&&o.push(null);for(y=0,S=o.length;y<S;y++){s=o[y],s||(s={id:null,name:"Other"}),e=n(this.groupTemplate(s)),this.$el.append(e),t=e.find(".accordian-body ul"),d=v[s.id],p=r.sortBy(d.categories,"order"),d[null]&&p.push(null);for(b=0,x=p.length;b<x;b++){h=p[b],h?(u=h.id,c=h.name):(u=null,c="Other"),t.append("<li class=nav-header>"+c+"</li>"),t.append("<li class=divider>"+c+"</li>"),l=d[u];for(w=0,T=l.length;w<T;w++)f=l[w],m=new a({model:f}),t.append(m.render())}p.length===1&&(t.find(".nav-header").remove(),t.find(".divider").remove())}return o.length===1&&(e.find(".accordian-heading").remove(),e.find(".accordian-body").removeClass("collapse")),this.$el},t.prototype.toggleCaret=function(e){var t;return t=n(e.target),t.siblings(".caret").toggleClass("closed")},t}(i.View),p=function(e){function t(){return g=t.__super__.constructor.apply(this,arguments),g}return __extends(t,e),t.prototype.template=r.template("            <form id=data-filters-search class=form-search action=>                <input type=text class=search-query placeholder=Search>            </form>        "),t.prototype.events={"keyup input":"autocomplete",submit:"search"},t.prototype.initialize=function(){return this.setElement(this.template())},t.prototype.autocomplete=function(){},t.prototype.search=function(){},t}(i.View),h=function(e){function t(){return y=t.__super__.constructor.apply(this,arguments),y}return __extends(t,e),t.prototype.template=r.template('            <div id=data-filters-panel class="panel panel-left scrollable-column closed">                <div class="inner panel-content"></div>                <div class=panel-toggle></div>            </div>        '),t.prototype.initialize=function(e){var t;return this.setElement(this.template()),t=this.$(".panel-content"),this.browser=new c({collection:this.collection}),e.enableSearch&&(this.form=new p({collection:this.collection}),t.append(this.form.el)),t.append(this.browser.el),n("body").append(this.$el),this.$el.panel()},t}(i.View),l=function(e){function i(){return this.render=__bind(this.render,this),b=i.__super__.constructor.apply(this,arguments),b}return __extends(i,e),i.prototype.events={"click [data-toggle=clear]":"clear"},i.prototype.template=r.template('            <div id=data-filters-list-panel class="panel panel-right scrollable-column closed">                <div class="inner panel-content">                    <div class=actions>                        <button data-route="review/" class="btn btn-small btn-primary">View Results</button>                        <button data-toggle=clear class="btn btn-small btn-danger pull-right" title="Clear All">                            <i class="icon-ban-circle icon-white"></i>                        </button>                    </div>                    <div class=filters></div>                </div>                <div class=panel-toggle></div>            </div>        '),i.prototype.initialize=function(e){var r=this;return this.setElement(this.template()),this.$filters=this.$(".filters"),n("body").append(this.$el),this.$el.panel(),t.subscribe(s.DATACONTEXT_SYNCING,function(){return r.$filters.addClass("loading")}),t.subscribe(s.DATACONTEXT_SYNCED,function(e){if(e.isSession())return r.render(e)})},i.prototype._parse=function(e,t){var n,r,i,s;t==null&&(t=[]);if(e.children){t.push("<ul><li class=nav-header>"+e.type+"'ed</li>"),s=e.children;for(r=0,i=s.length;r<i;r++)n=s[r],this._parse(n,t);t.push("</ul>")}else t.length||t.push("<ul>"),t.push("<li>"+e.language+"</li>"),t.length||t.push("</ul>");return t},i.prototype.render=function(e){var t,i;return this.$filters.empty(),this.$filters.removeClass("loading"),t=e.get("language"),!t||r.isEmpty(t)?this.$filters.append('                    <div class=muted>                        <h4>No filters are applied</h4>                        <p>Explore the available filters on the left side                            or click "View Results" to immediately see some                            data.</p>                    </div>                '):(i=n(this._parse(t).join("")).addClass("unstyled nav-list"),this.$filters.append(i)),this.$el},i.prototype.clear=function(e){return e.preventDefault(),t.publish(s.DATACONTEXT_CLEAR)},i}(i.View),{View:f,Panel:h,SearchForm:p,Accordian:c,List:l}});