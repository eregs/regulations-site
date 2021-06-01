import Dropdown from '../components/Dropdown.vue';
import DropdownContent from '../components/DropdownContent.vue';
import DropdownItem from '../components/DropdownItem.vue';

export default {
  title: 'Dropdown/Dropdown',
  component: Dropdown,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { Dropdown, DropdownContent, DropdownItem},
  template: '<dropdown v-bind="$props" v-slot="{ active }"><dropdown-content :active="active"><dropdown-item>2020-03-01</dropdown-item></dropdown-content></dropdown>',
});

export const Basic = Template.bind({});
Basic.args = {
  initialActive: false,
};
