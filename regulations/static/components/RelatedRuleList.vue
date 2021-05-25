<template>
    <div class="related-rule-list">
        <related-rule v-for="(rule, index) in rules" :key="index"
            :title="rule.title"
            :type="rule.type"
            :citation="rule.citation"
            :effective_on="rule.effective_on"
            :document_number="rule.document_number"
            :html_url="rule.html_url">
        </related-rule>
    </div>
</template>

<script>
import RelatedRule from './RelatedRule.vue'
export default {
    name: 'related-rule-list',

    components: {
        RelatedRule,
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
</script>
