var __bind=function(e,t){return function(){return e.apply(t,arguments)}},__hasProp={}.hasOwnProperty,__extends=function(e,t){function r(){this.constructor=e}for(var n in t)__hasProp.call(t,n)&&(e[n]=t[n]);return r.prototype=t.prototype,e.prototype=new r,e.__super__=t.prototype,e};define(["environ","mediator","jquery","underscore","backbone","./utils","./backbone-charts"],function(e,t,n,r,i,s){var o,u,a,f,l;return a=r.template('        <div class="area-container chart-container">            <div class=btn-toolbar>                <div class=btn-group>                    <button class="btn btn-mini fullsize" title="Toggle Fullsize"><i class=icon-resize-full alt="Toggle Fullsize"></i></button>                    <!--<button class="btn btn-mini outliers" title="Show Outliers" disabled><i class=icon-eye-open alt="Show Outliers"></i></button>-->                </div>                <div class=btn-group>                    <button class="btn btn-mini edit" title="Edit"><i class=icon-wrench alt="Edit"></i></button>                </div>                <div class=btn-group>                    <button class="btn btn-danger btn-mini remove" title="Remove"><i class=icon-remove alt="Remove"></i></button>                </div>            </div>            <div class=heading>                <span class="label label-info"></span>            </div>            <div class=editable>                <form class=form>                    <fieldset>                        <label>X-Axis <select name=x-axis></select></label>                        <label>Y-Axis <select name=y-axis></select></label>                        <label>Series <select name=series></select></label>                        <button class="btn btn-primary">Update</button>                    </fieldset>                </form>            </div>            <div class=chart>            </div>        </div>    '),o=function(e){function t(){return this.render=__bind(this.render,this),f=t.__super__.constructor.apply(this,arguments),f}return __extends(t,e),t.prototype.tagName="select",t.prototype.options={enumerableOnly:!1},t.prototype.initialize=function(){return this.collection.when(this.render)},t.prototype.render=function(){var e,t,n,r;this.$el.append("<option value=>---</option>"),r=this.collection.models;for(t=0,n=r.length;t<n;t++){e=r[t];if(e.get("searchable"))continue;if(this.options.enumerableOnly&&!e.get("enumerable"))continue;this.$el.append('<option value="'+e.id+'">'+e.get("name")+"</option>")}return this.$el},t.prototype.getSelected=function(){return this.collection.get(parseInt(this.$el.val()))},t}(i.View),u=function(e){function t(){return l=t.__super__.constructor.apply(this,arguments),l}return __extends(t,e),t.prototype.options={editable:!0},t.prototype.events={mouseenter:"showToolbar",mouseleave:"hideToolbar","click .fullsize":"toggleExpanded","click .outliers":"toggleOutliers","click .edit":"toggleEdit","click .remove":"removeChart",submit:"changeChart","change .editable select":"disableSelected"},t.prototype.initialize=function(){var e;t.__super__.initialize.apply(this,arguments),this.setElement(a()),this.$heading=this.$(".heading"),this.$label=this.$heading.find(".label"),this.$renderArea=this.$(".chart"),this.$toolbar=this.$(".btn-toolbar"),this.$fullsizeToggle=this.$(".fullsize"),this.$form=this.$(".editable");if(this.options.editable===!1)return this.$form.detach(),this.$toolbar.detach();this.xAxis=new o({el:this.$el.find("[name=x-axis]"),collection:this.collection}),this.yAxis=new o({el:this.$el.find("[name=y-axis]"),collection:this.collection}),this.series=new o({el:this.$el.find("[name=series]"),enumerableOnly:!0,collection:this.collection});if(this.model)return this.model.get("xAxis")&&this.$form.hide(),(e=this.model.get("expanded"))?this.expand():this.contract()},t.prototype.render=function(){return this.$el},t.prototype.renderChart=function(e){var t,r;this.chart&&typeof (r=this.chart).destroy=="function"&&r.destroy(),this.$label.detach(),this.$heading.text(e.title.text),e.title.text="";if(!e.series[0]){this.$renderArea.html("<p class=no-data>Unfortunately, there is                    no data to graph here.</p>");return}return this.$form.hide(),t=[],e.clustered&&t.push("Clustered"),t[0]&&(this.$label.text(t.join(", ")).show(),this.$heading.append(this.$label)),n.extend(!0,e,this.chartOptions),e.chart.renderTo=this.$renderArea[0],this.chart=new Highcharts.Chart(e),this},t.prototype.disableSelected=function(e){var t,r;t=n(e.target),this.xAxis.el===e.target?(this.yAxis.$("option").prop("disabled",!1),this.series.$("option").prop("disabled",!1)):this.yAxis.el===e.target?(this.xAxis.$("option").prop("disabled",!1),this.series.$("option").prop("disabled",!1)):(this.xAxis.$("option").prop("disabled",!1),this.yAxis.$("option").prop("disabled",!1));if((r=t.val())!=="")return this.xAxis.el===e.target?(this.yAxis.$("option[value="+r+"]").prop("disabled",!0).val(""),this.series.$("option[value="+r+"]").prop("disabled",!0).val("")):this.yAxis.el===e.target?(this.xAxis.$("option[value="+r+"]").prop("disabled",!0).val(""),this.series.$("option[value="+r+"]").prop("disabled",!0).val("")):(this.xAxis.$("option[value="+r+"]").prop("disabled",!0).val(""),this.yAxis.$("option[value="+r+"]").prop("disabled",!0).val(""))},t.prototype.toggleExpanded=function(e){var t;return t=this.model.get("expanded"),t?this.contract():this.expand(),this.model.save({expanded:!t})},t.prototype.resize=function(){var e;e=this.$renderArea.width();if(this.chart)return this.chart.setSize(e,null,!1)},t.prototype.expand=function(){return this.$fullsizeToggle.children("i").removeClass("icon-resize-small").addClass("icon-resize-full"),this.$el.addClass("expanded"),this.resize()},t.prototype.contract=function(){return this.$fullsizeToggle.children("i").removeClass("icon-resize-full").addClass("icon-resize-small"),this.$el.removeClass("expanded"),this.resize()},t.prototype.hideToolbar=function(){return this.$toolbar.fadeOut(200)},t.prototype.showToolbar=function(){return this.$toolbar.fadeIn(200)},t.prototype.toggleOutliers=function(e){var t,n,r,i,s;i=this.chart.series,s=[];for(n=0,r=i.length;n<r;n++){t=i[n];continue}return s},t.prototype.toggleEdit=function(e){return this.$form.is(":visible")?this.$form.fadeOut(300):this.$form.fadeIn(300)},t.prototype.removeChart=function(e){var t;this.chart&&typeof (t=this.chart).destroy=="function"&&t.destroy(),this.$el.remove();if(this.model)return this.model.destroy()},t.prototype.update=function(e,t,n,r){var o,u,a,f=this;if(this.options.data){a=this.options.data;for(o in a)u=a[o],t?t+="&"+o+"="+u:t=""+o+"="+u}return this.$el.addClass("loading"),i.ajax({url:e,data:t,success:function(e){return f.$el.removeClass("loading"),f.renderChart(s.processResponse(e,n,r))}})},t.prototype.changeChart=function(e){var t=this;return e&&e.preventDefault(),this.collection.when(function(){var n,r,i,s,o,u,a;e==null&&((u=t.model.get("xAxis"))&&t.xAxis.$el.val(u.toString()),(a=t.model.get("yAxis"))&&t.yAxis.$el.val(a.toString()),(i=t.model.get("series"))&&t.series.$el.val(i.toString())),u=t.xAxis.getSelected(),a=t.yAxis.getSelected(),i=t.series.getSelected();if(!u)return;return o=t.model.get("_links").distribution.href,r=[u],n="dimension="+u.id,a&&(r.push(a),n=n+"&dimension="+a.id),i&&(s=a?2:1,n=n+"&dimension="+i.id),e&&t.model&&t.model.set({xAxis:u.id,yAxis:a?a.id:void 0,series:i?i.id:void 0}),t.update(o,n,r,s)})},t}(i.Chart),{DistributionChart:u}});