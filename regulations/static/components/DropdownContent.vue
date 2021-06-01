<template>
  <div v-if="active" class="dropdown-content">
    <slot />
  </div>
</template>

<script>
export default {
  name: 'dropdown-content',
  props: {
    active: {
      type: Boolean,
      default: false
    },
  },
}
</script>
