import PartButton from '../components/PartButton.vue'

export default {
  title: 'Button/Part Button',
  component: PartButton,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { PartButton },
  template: '<part-button v-bind="$props" ></part-button>',
});

export const Basic = Template.bind({});
Basic.args = {
};
