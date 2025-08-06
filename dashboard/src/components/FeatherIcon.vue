<template>
  <i :class="iconClass" :style="{ width: size, height: size }"></i>
</template>

<script>
export default {
  name: 'FeatherIcon',
  props: {
    name: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: '16px',
    },
  },
  computed: {
    iconClass() {
      return `feather feather-${this.name}`;
    },
  },
};
</script> 