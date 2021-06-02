<template>
  <div>
    <slot name="toggler">
      <button class="ds-c-field" @click="toggle">Toggle</button>
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
