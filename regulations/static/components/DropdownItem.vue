<template>
  <a v-bind:href="url" class="dropdown-item">
    <slot />
  </a>
</template>

<script>
  export default {
    name: "dropdown-item"
  };
</script>
