import RelatedRule from '../components/RelatedRule.vue';

export default {
  title: 'SupplementaryContent/Related Rule',
  component: RelatedRule,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { RelatedRule },
  template: '<related-rule v-bind="$props" ></related-rule>',
});

export const Basic = Template.bind({});
Basic.args = {
  "title": "Medicaid Program; Establishing Minimum Standards in Medicaid State Drug Utilization Review (DUR) and Supporting Value-Based Purchasing (VBP) for Drugs Covered in Medicaid, Revising Medicaid Drug Rebate and Third Party Liability (TPL) Requirements",
  "type": "Rule",
  "citation": "85 FR 87000",
  "effective_on": "2021-03-01",
  "document_number": "2020-28567",
  "html_url": "https://www.federalregister.gov/documents/2020/12/31/2020-28567/medicaid-program-establishing-minimum-standards-in-medicaid-state-drug-utilization-review-dur-and"
};