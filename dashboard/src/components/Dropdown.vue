<template>
  <div class="relative">
    <slot
      :toggleDropdown="toggleDropdown"
      :highlightItemUp="highlightItemUp"
      :highlightItemDown="highlightItemDown"
      :selectHighlightedItem="selectHighlightedItem"
    />
    <div
      v-if="isOpen"
      class="absolute z-50 mt-1 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5"
      :class="right ? 'right-0' : 'left-0'"
    >
      <div class="py-1">
        <button
          v-for="(item, index) in items"
          :key="index"
          class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
          :class="{ 'bg-gray-100 dark:bg-gray-700': highlightedIndex === index }"
          @click="selectItem(item)"
          @mouseenter="highlightedIndex = index"
        >
          {{ item.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dropdown',
  props: {
    items: {
      type: Array,
      default: () => [],
    },
    right: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isOpen: false,
      highlightedIndex: -1,
    };
  },
  methods: {
    toggleDropdown(force = null) {
      if (force !== null) {
        this.isOpen = force;
      } else {
        this.isOpen = !this.isOpen;
      }
      if (!this.isOpen) {
        this.highlightedIndex = -1;
      }
    },
    highlightItemUp() {
      if (this.highlightedIndex > 0) {
        this.highlightedIndex--;
      } else {
        this.highlightedIndex = this.items.length - 1;
      }
    },
    highlightItemDown() {
      if (this.highlightedIndex < this.items.length - 1) {
        this.highlightedIndex++;
      } else {
        this.highlightedIndex = 0;
      }
    },
    selectHighlightedItem() {
      if (this.highlightedIndex >= 0 && this.highlightedIndex < this.items.length) {
        this.selectItem(this.items[this.highlightedIndex]);
      }
    },
    selectItem(item) {
      if (item.action) {
        item.action();
      }
      this.toggleDropdown(false);
    },
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!this.$el.contains(e.target)) {
        this.toggleDropdown(false);
      }
    });
  },
};
</script> 