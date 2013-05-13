define(["jquery", "underscore", "backbone", "regs-data", "definition-view", "interpretation-view"], function($, _, Backbone, RegsData,  DefinitionView, InterpretationView) {
    "use strict";
    return {
        getTree: function($obj) {
            var parent = this;
            $obj.children().each(function() {
                var $child = $(this),
                    cid = $child.attr('id'),
                    clist = $child.find('ol'),
                    $nextChild;

                RegsData.store({
                    'text': cid,
                    'content': $child.html()
                }); 

                if (typeof (cid, clist) !== 'undefined') {
                    $nextChild = clist ? $(clist) : $child;
                    parent.getTree($nextChild);
                }
            });
        },

        bindEvents: function() {
            // fake template
            var template = function(b, p) {
                $('#' + p).append(b);
            };

            /* 
            * EVENT BINDINGS 
            */
            // click term link, open definition
            $('.definition').on('click', function(e) {
                e.preventDefault();
                var defId = $(this).attr('data-definition');

                // briefly considered giving the term link its own view
                // decided that it was unecessary for now. if this event
                // binding section gets out of hand, we should reconsider [ts]

                // TODO: supports only one open definition
                if (!RegsViews.openDefinitions[defId]) {
                    RegsViews.openDefinitions[defId] = new DefinitionView({
                        id: defId,
                        $anchor: $(e.target)
                    });
                }
                else {
                    RegsViews.openDefinitions[defId].remove();
                    delete(RegsViews.openDefinitions[defId]);
                }
            });

            // mimics 'read more' accordion type thing
            $('.expand').on('click', function(e) {
                e.preventDefault();
                var pid = $(this).parent().attr('id'),
                    body = RegsData.retrieve(pid); 
                template(body, pid);

                $(this).remove();
            });

            $('.interpretation-ref').on('click', function(e) {
                e.preventDefault();
                var $domContext = $(this),
                    parent = $domContext.closest('li').attr('id'),
                    interpretationId = "I-" + parent;

                if (!RegsViews.openInterpretations[interpretationId]) {
                    RegsViews.openInterpretations[interpretationId] = new InterpretationView({
                        id: interpretationId,
                        $anchor: $domContext
                    });
                }
                else {
                    RegsViews.openInterpretations[interpretationId].remove();
                    delete(RegsViews.openInterpretations[interpretationId]);                    
                }
            });
        },

        init: function() {
            this.getTree($('#reg-content')); 
            this.bindEvents();
            console.log(RegsData);
        }
    }
});
