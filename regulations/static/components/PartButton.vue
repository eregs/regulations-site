<template>
  <button
    v-on-clickaway="away"
    class="dropdown-part-button"
    @click="toggle"
  >
    Part <i class="fas fa-chevron-down" />
  </button>
</template>

<script>
import { mixin as clickaway } from 'vue-clickaway';

export default {
  name: 'part-button',
  mixins: [clickaway],
  props: {
    toggle: {type: Function},
    away: {type: Function}
  }
}
</script>
