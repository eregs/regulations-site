import Dropdown from '../components/Dropdown.vue';
import DropdownContent from '../components/DropdownContent.vue';
import DropdownHeader from '../components/DropdownHeader.vue';
import DropdownItem from '../components/DropdownItem.vue';

export default {
  title: 'Dropdown/Dropdown',
  component: Dropdown,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { Dropdown, DropdownContent, DropdownHeader, DropdownItem},
  template: `
    <dropdown v-bind="$props" v-slot="{ active }">
      <dropdown-content :active="active">
        <dropdown-header>Regulation Change</dropdown-header>
        <dropdown-item>Mar 1, 2021</dropdown-item>
        <dropdown-item>Jan 1, 2020</dropdown-item>
        <dropdown-item>May 3, 2019</dropdown-item>
      </dropdown-content>
    </dropdown>
  `,
});

export const Basic = Template.bind({});
Basic.args = {
  initialActive: false,
};
