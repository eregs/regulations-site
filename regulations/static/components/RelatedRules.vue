<template>
    <div>
        <related-rule-list :rules="rules"></related-rule-list>
    </div>
</template>

<script>
import RelatedRuleList from './RelatedRuleList.vue'
export default {
    components: {
        RelatedRuleList,
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
</script>
