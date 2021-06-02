<template>
  <li class="dropdown-item">
    <a v-bind:href="href" class="dropdown-link">
      <slot />
    </a>
  </li>
</template>

<script>
  export default {
    name: "dropdown-item"
  };
</script>
