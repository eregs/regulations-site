// this is a browserify friendly version of https://github.com/ssorallen/jquery-scrollstop


const $ = require('jquery');

const dispatch = $.event.dispatch || $.event.handle;

const special = $.event.special;
const uid1 = `D${+new Date()}`;
const uid2 = `D${+new Date() + 1}`;

special.scrollstart = {
  setup: function setup(initialData) {
    const data = $.extend({
      latency: special.scrollstop.latency,
    }, initialData);

    let timer;
    const handler = function handler(evt, ...args) {
      const self = this;

      if (timer) {
        clearTimeout(timer);
      } else {
        const modifiedEvent = $.Event(null, evt);
        modifiedEvent.type = 'scrollstart';
        dispatch.apply(self, [modifiedEvent].concat(args));
      }

      timer = setTimeout(() => {
        timer = null;
      }, data.latency);
    };

    $(this).bind('scroll', handler).data(uid1, handler);
  },
  teardown: function teardown() {
    $(this).unbind('scroll', $(this).data(uid1));
  },
};

special.scrollstop = {
  latency: 250,
  setup: function setup(initialData) {
    const data = $.extend({
      latency: special.scrollstop.latency,
    }, initialData);

    let timer;
    const handler = function handler(evt, ...args) {
      const self = this;

      if (timer) {
        clearTimeout(timer);
      }

      timer = setTimeout(() => {
        timer = null;
        const modifiedEvent = $.Event(null, evt);
        modifiedEvent.type = 'scrollstop';
        dispatch.apply(self, [modifiedEvent].concat(args));
      }, data.latency);
    };
    $(this).bind('scroll', handler).data(uid2, handler);
  },
  teardown: function teardown() {
    $(this).unbind('scroll', $(this).data(uid2));
  },
};
