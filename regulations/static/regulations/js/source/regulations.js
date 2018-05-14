// Launches app
import { createStore } from 'redux';
import { setStorage } from './redux/storage';
import reducers from './redux/reducers';

setStorage(createStore(reducers));


// make jQuery globally accessible for plugins and analytics
window.$ = window.jQuery = require('jquery');
const app = require('./app-init');

// A `bind()` polyfill
if (!Function.prototype.bind) {
  /* eslint-disable no-extend-native */
  Function.prototype.bind = function bind(oThis, ...aArgs) {
    if (typeof this !== 'function') {
            // closest thing possible to the ECMAScript 5 internal IsCallable function
      throw new TypeError('Function.prototype.bind - what is trying to be bound is not callable');
    }

    const fToBind = this;
    const FNOP = function FNOP() {};
    const fBound = function fBound(...args) {
      const arg1 = this instanceof FNOP && oThis ? this : oThis;
      const arg2 = aArgs.concat(args);
      return fToBind.apply(arg1, arg2);
    };

    FNOP.prototype = this.prototype;
    fBound.prototype = new FNOP();

    return fBound;
  };
  /* eslint-enable */
}

// a 'window.location.origin' polyfill for IE10
// http://tosbourn.com/2013/08/javascript/a-fix-for-window-location-origin-in-internet-explorer/
if (!window.location.origin) {
  window.location.origin = `${window.location.protocol}//${window.location.hostname}${window.location.port ? `:${window.location.port}` : ''}`;
}

$(document).ready(() => {
  app.init();
});

// tests for some accessibility misses
// use in browser console with AccessibilityTest()
window.AccessibilityTest = function AccessibilityTest() {
    /* eslint-disable */
    // I think this will keep IE from crying?
    console = console || {error: function() {}};

    $('img').each(function() {
        if (typeof this.attributes.alt === 'undefined') {
            console.error('Image does not have alt text', this);
        }
    });

    $('p, h1, h2, h3, h4, h5, h6, div, span').each(function() {
        if ($(this).css('font-size').indexOf('em') === -1 && $(this).css('font-size').indexOf('px') > 0) {
            console.error('Font size is set in px, not ems', this);
        }
    });
    /* eslint-enable */
};
