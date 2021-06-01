import DropdownContent from '../components/DropdownContent.vue';
import DropdownItem from '../components/DropdownItem.vue'

export default {
  title: 'Dropdown/Dropdown Content',
  component: DropdownContent,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { DropdownContent, DropdownItem },
  template: '<dropdown-content v-bind="$props"><dropdown-item>2020-03-01</dropdown-item><dropdown-item>2020-01-01</dropdown-item></dropdown-content>',
});

export const Basic = Template.bind({});
Basic.args = {
  active: true,
};
