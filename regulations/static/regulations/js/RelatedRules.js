//
//
//
//
//
//
//
//
//
//
//
//


var script$2 = {
  name: 'related-rule',

  props: {
    title: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
    citation: {
      type: String,
      required: true,
    },
    effective_on: String,
    document_number: {
      type: String,
      required: true,
    },
    html_url: {
      type: String,
      required: true,
    },
  },

  computed: {
    expandedType: function() {
      if(this.type === "Rule") {
        return "Final";
      }
      return "Unknown";
    },
  },

  methods: {},
  filters: {
    formatDate: function(value) {
      const date = new Date(value);
      const options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };
      const format = new Intl.DateTimeFormat("en-US", options);
      return format.format(date);
    } 
  }
};

function normalizeComponent(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
    if (typeof shadowMode !== 'boolean') {
        createInjectorSSR = createInjector;
        createInjector = shadowMode;
        shadowMode = false;
    }
    // Vue.extend constructor export interop.
    const options = typeof script === 'function' ? script.options : script;
    // render functions
    if (template && template.render) {
        options.render = template.render;
        options.staticRenderFns = template.staticRenderFns;
        options._compiled = true;
        // functional template
        if (isFunctionalTemplate) {
            options.functional = true;
        }
    }
    // scopedId
    if (scopeId) {
        options._scopeId = scopeId;
    }
    let hook;
    if (moduleIdentifier) {
        // server build
        hook = function (context) {
            // 2.3 injection
            context =
                context || // cached call
                    (this.$vnode && this.$vnode.ssrContext) || // stateful
                    (this.parent && this.parent.$vnode && this.parent.$vnode.ssrContext); // functional
            // 2.2 with runInNewContext: true
            if (!context && typeof __VUE_SSR_CONTEXT__ !== 'undefined') {
                context = __VUE_SSR_CONTEXT__;
            }
            // inject component styles
            if (style) {
                style.call(this, createInjectorSSR(context));
            }
            // register component module identifier for async chunk inference
            if (context && context._registeredComponents) {
                context._registeredComponents.add(moduleIdentifier);
            }
        };
        // used by ssr in case component is cached and beforeCreate
        // never gets called
        options._ssrRegister = hook;
    }
    else if (style) {
        hook = shadowMode
            ? function (context) {
                style.call(this, createInjectorShadow(context, this.$root.$options.shadowRoot));
            }
            : function (context) {
                style.call(this, createInjector(context));
            };
    }
    if (hook) {
        if (options.functional) {
            // register for functional component in vue file
            const originalRender = options.render;
            options.render = function renderWithStyleInjection(h, context) {
                hook.call(context);
                return originalRender(h, context);
            };
        }
        else {
            // inject component registration as beforeCreate hook
            const existing = options.beforeCreate;
            options.beforeCreate = existing ? [].concat(existing, hook) : [hook];
        }
    }
    return script;
}

/* script */
const __vue_script__$2 = script$2;

/* template */
var __vue_render__$2 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c("div", { staticClass: "related-rule" }, [
    _c("div", { staticClass: "related-rule-header" }, [
      _c(
        "span",
        { staticClass: "related-rule-type ds-c-badge ds-c-badge--final" },
        [_vm._v(_vm._s(_vm.expandedType))]
      ),
      _vm._v(" "),
      _vm.effective_on
        ? _c("span", { staticClass: "related-rule-date" }, [
            _vm._v(_vm._s(_vm._f("formatDate")(_vm.effective_on)))
          ])
        : _vm._e(),
      _c("span", { staticClass: "related-rule-citation" }, [
        _vm._v(_vm._s(_vm.citation))
      ])
    ]),
    _vm._v(" "),
    _c("div", [
      _c(
        "a",
        { staticClass: "related-rule-title", attrs: { href: _vm.html_url } },
        [
          _vm._v(_vm._s(_vm.title) + " "),
          _c("i", { staticClass: "fas fa-external-link-alt" })
        ]
      )
    ])
  ])
};
var __vue_staticRenderFns__$2 = [];
__vue_render__$2._withStripped = true;

  /* style */
  const __vue_inject_styles__$2 = undefined;
  /* scoped */
  const __vue_scope_id__$2 = undefined;
  /* module identifier */
  const __vue_module_identifier__$2 = undefined;
  /* functional template */
  const __vue_is_functional_template__$2 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$2 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$2, staticRenderFns: __vue_staticRenderFns__$2 },
    __vue_inject_styles__$2,
    __vue_script__$2,
    __vue_scope_id__$2,
    __vue_is_functional_template__$2,
    __vue_module_identifier__$2,
    false,
    undefined,
    undefined,
    undefined
  );

//
var script$1 = {
    name: 'related-rule-list',

    components: {
        RelatedRule: __vue_component__$2,
    },

    props: {
        rules: Array,
    },

    computed: {

    },

    methods: {

    },

    filters: {

    },
};

/* script */
const __vue_script__$1 = script$1;

/* template */
var __vue_render__$1 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "div",
    { staticClass: "related-rule-list" },
    _vm._l(_vm.rules, function(rule, index) {
      return _c("related-rule", {
        key: index,
        attrs: {
          title: rule.title,
          type: rule.type,
          citation: rule.citation,
          effective_on: rule.effective_on,
          document_number: rule.document_number,
          html_url: rule.html_url
        }
      })
    }),
    1
  )
};
var __vue_staticRenderFns__$1 = [];
__vue_render__$1._withStripped = true;

  /* style */
  const __vue_inject_styles__$1 = undefined;
  /* scoped */
  const __vue_scope_id__$1 = undefined;
  /* module identifier */
  const __vue_module_identifier__$1 = undefined;
  /* functional template */
  const __vue_is_functional_template__$1 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$1 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$1, staticRenderFns: __vue_staticRenderFns__$1 },
    __vue_inject_styles__$1,
    __vue_script__$1,
    __vue_scope_id__$1,
    __vue_is_functional_template__$1,
    __vue_module_identifier__$1,
    false,
    undefined,
    undefined,
    undefined
  );

//
var script = {
    components: {
        RelatedRuleList: __vue_component__$1,
    },
    
    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
    },
    
    data() {
        return {
            rules: null,
        }
    },

    async created() {
        this.rules = await this.fetch_rules(this.title, this.part);
    },
    
    methods: {
        async fetch_rules(title, part) {
            const response = await fetch(`https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&per_page=20&conditions[type][]=RULE&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`);
            const rules = await response.json();
            return rules.results;
        }
    }
};

/* script */
const __vue_script__ = script;

/* template */
var __vue_render__ = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "div",
    [_c("related-rule-list", { attrs: { rules: _vm.rules } })],
    1
  )
};
var __vue_staticRenderFns__ = [];
__vue_render__._withStripped = true;

  /* style */
  const __vue_inject_styles__ = undefined;
  /* scoped */
  const __vue_scope_id__ = undefined;
  /* module identifier */
  const __vue_module_identifier__ = undefined;
  /* functional template */
  const __vue_is_functional_template__ = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__ = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__, staticRenderFns: __vue_staticRenderFns__ },
    __vue_inject_styles__,
    __vue_script__,
    __vue_scope_id__,
    __vue_is_functional_template__,
    __vue_module_identifier__,
    false,
    undefined,
    undefined,
    undefined
  );

export default __vue_component__;
