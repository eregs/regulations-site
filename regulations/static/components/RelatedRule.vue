<template>
  <div class="related-rule">
    <div class="related-rule-header">
      <span class="related-rule-type indicator">{{ expandedType }}</span>
      <span class="related-rule-date" v-if="effective_on">{{ effective_on|formatDate }}</span><span class="related-rule-citation">{{ citation }}</span>
    </div>
    <div>
      <a class="related-rule-title external" :href="html_url">{{ title }}</a>
    </div>
  </div>
</template>

<script>

export default {
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
</script>
