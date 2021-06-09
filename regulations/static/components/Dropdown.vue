<template>
  <div>
    <slot name="toggler" v-bind:toggle="toggle">
      <button
        v-on-clickaway="away"
        class="dropdown-button ds-c-field" 
        @click="toggle"
      >
        {{ selection }}
      </button>
    </slot>
    <slot v-bind:active="active"/>
  </div>
</template>

<script>
import { mixin as clickaway } from 'vue-clickaway';

export default {
  name: 'Dropdown',
  mixins: [clickaway],
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
    },
    away() {
      this.active = false
    }
  }
}
</script>
