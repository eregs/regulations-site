define("header-view",["jquery","underscore","backbone","dispatch"],function(e,t,n,r){var i=n.View.extend({el:".reg-header",initialize:function(){this.$activeEls=e("#menu, #site-header, #content-body, #primary-footer"),this.$tocLinks=e(".toc-nav-link")},events:{"click .toc-toggle":"openDrawer","click .toc-nav-link":"toggleDrawerTab"},updateDrawerState:function(t){typeof this.$activeEls!="undefined"&&(r.trigger("toc:toggle",t+" toc"),e("#panel-link").toggleClass("open"),this.$activeEls.toggleClass("active"))},openDrawer:function(t){t.preventDefault();var n=e(t.target),r=n.hasClass("open")?"close":"open";this.updateDrawerState(r)},toggleDrawerTab:function(n){n.preventDefault();var i=e(n.target),s=t.last(i.closest("a").attr("href").split("#"));this.$tocLinks.removeClass("current"),i.closest("a").addClass("current"),e(".panel").css("left")==="-200px"&&this.updateDrawerState("open"),r.trigger("drawer:stateChange",s)}});return i});