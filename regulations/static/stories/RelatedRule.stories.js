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
  "type":"Rule",
  "abstract":"This final rule will advance CMS' efforts to support state flexibility to enter into innovative value-based purchasing arrangements (VBPs) with manufacturers, and to provide manufacturers with regulatory support to enter into VBPs with payers, including Medicaid. To ensure that the regulatory framework is sufficient to support such arrangements and to promote transparency, flexibility, and innovation in drug pricing without undue administrative burden, we are finalizing new regulatory policies and clarifying certain already established policies to assist manufacturers and states in participating in VBPs in a manner that is consistent with the law and maintains the integrity of the Medicaid Drug Rebate Program (MDRP). This final rule also revises regulations regarding: Authorized generic sales when manufacturers calculate average manufacturer price (AMP) for the brand name drug; pharmacy benefit managers (PBM) accumulator programs and their impact on AMP and best price when manufacturer- sponsored assistance is not passed through to the patient; state and manufacturer reporting requirements to the MDRP; new Medicaid Drug Utilization Review (DUR) provisions designed to reduce opioid related fraud, misuse and abuse; the definitions of CMS-authorized supplemental rebate agreement, line extension, new formulation, oral solid dosage form, single source drug, multiple source drug, innovator multiple source drug for purposes of the MDRP; payments for prescription drugs under the Medicaid program; and coordination of benefits (COB) and third party liability (TPL) rules related to the special treatment of certain types of care and payment in Medicaid and Children's Health Insurance Program (CHIP).",
  "document_number":"2020-28567",
  "html_url":"https://www.federalregister.gov/documents/2020/12/31/2020-28567/medicaid-program-establishing-minimum-standards-in-medicaid-state-drug-utilization-review-dur-and"
};