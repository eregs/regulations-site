define("meta-model",["underscore","backbone","dispatch"],function(e,t,n){var r=t.Model.extend({constructor:function(e){var n;if(typeof e!="undefined")for(n in e)e.hasOwnProperty(n)&&(this[n]=e[n]);this.content=this.content||{},this.structure=this.structure||[],t.Model.apply(this,arguments)},set:function(t,n){var r=this.has(t),i;return typeof t!="undefined"&&!e.isEmpty(t)&&(r?i=r:(this.content[t]=n,i=n,e.indexOf(this.structure,t)===-1&&this.structure.push(t))),i},has:function(e){return this.content[e]?!0:!1},get:function(e,t){var r,i;return n.trigger("content:loading"),r=this.has(e)?this._retrieve(e):this.request(e),i=function(e){typeof t!="undefined"&&t(e),n.trigger("content:loaded")},r.done(i),r.fail(function(){var e=document.createElement("div");e.innerHTML="There was an issue loading your data. This may be because your device is currently offline. Please try again.",e.className="alert",$(e).insertBefore("h2.section-number"),n.trigger("content:loaded"),t.apply(!1)}),this},_retrieve:function(e){var t=$.Deferred();return t.resolve(this.content[e]),t.promise()},request:function(e){var t=this.getAJAXUrl(e),n;return n=$.ajax({url:t,success:function(t){this.set(e,t)}.bind(this)}),n},getAJAXUrl:function(e){var t,r=n.getURLPrefix();return r?t="/"+r+"/partial/":t="/partial/",typeof this.supplementalPath!="undefined"&&(t+=this.supplementalPath+"/"),t+=e,e.indexOf("/")===-1&&(t+="/"+n.getVersion()),t},sync:function(){return},save:function(){return},destroy:function(){return}});return r});