<template>
  <div>
    <slot name="toggler">
      <button class="dropdown-button ds-c-field" @click="toggle">{{ selection }}</button>
    </slot>
    <slot v-bind:active="active"/>
  </div>
</template>

<script>
export default {
  name: 'Dropdown',
  props: {
    initialActive: {
      type: Boolean,
      required: true,
      default: false
    },
    selection: {
      type: String,
      required: true,
      default: "Select Date"
    }
  },
  data() {
    return {
      active: this.initialActive
    }
  },
  methods: {
    toggle() {
      this.active = !this.active
    }
  }
}
</script>
