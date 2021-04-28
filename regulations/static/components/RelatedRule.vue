<template>
  <div>
    <h2><a :href="html_url">{{ title }}</a></h2>
    <p>{{ abstract }}</p>
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
    html_url: {
      type: String,
      required: true,
    },
    abstract: {
      type: String,
      required: true,
    },
  },

  computed: {},

  methods: {},
};
</script>
