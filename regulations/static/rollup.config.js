import vue from 'rollup-plugin-vue'

export default {
    // ...
    input: 'components/RelatedRules.vue',
    output: {
        format: 'esm',
        file: 'regulations/js/RelatedRules.js'
    },
    plugins: [
        // ...
        vue(/* options */)
    ]
}
