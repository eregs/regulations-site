import DropdownItem from '../components/DropdownItem.vue';

export default {
  title: 'Dropdown/Dropdown Item',
  component: DropdownItem,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { DropdownItem },
  template: '<dropdown-item v-bind="$props" >{{ slotcontent }}</dropdown-item>',
});

export const Basic = Template.bind({});
Basic.args = {
  url: "/433/Subpart-A/2021-03-01",
  slotcontent: "2020-03-01"
};
