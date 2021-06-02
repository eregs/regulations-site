<template>
  <div v-if="active" class="dropdown-content">
    <ul class="dropdown-list">
      <slot />
    </ul>
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
