import Dropdown from '../components/Dropdown.vue';
import DropdownContent from '../components/DropdownContent.vue';
import DropdownHeader from '../components/DropdownHeader.vue';
import DropdownItem from '../components/DropdownItem.vue';
import PartButton from '../components/PartButton.vue';

export default {
  title: 'Dropdown/Dropdown',
  component: Dropdown,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { Dropdown, DropdownContent, DropdownHeader, DropdownItem, PartButton},
  template: `
    <div>
      <dropdown v-bind="$props">
        <template v-if="${'partButton' in args}" v-slot:toggler="{ toggle, away }">${args.partButton}</template>
        <template v-slot:default="{ active }">
          <dropdown-content :active="active">
            <dropdown-header>Regulation Change</dropdown-header>
            <dropdown-item>Mar 1, 2021</dropdown-item>
            <dropdown-item>Jan 1, 2020</dropdown-item>
            <dropdown-item>May 3, 2019</dropdown-item>
          </dropdown-content>
        </template>
      </dropdown>
    </div>
  `,
});

export const WithRegularDropdown = Template.bind({});
WithRegularDropdown.args = {
  initialActive: false,
};

export const WithPartButton = Template.bind({});
WithPartButton.args = {
  initialActive: false,
  partButton: `<part-button :toggle="toggle" :away="away"></part-button>`
};