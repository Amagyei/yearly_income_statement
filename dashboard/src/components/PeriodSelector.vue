<template>
  <Dropdown ref="dropdown" class="text-sm" :items="periodOptions" right>
    <template
      #default="{
        toggleDropdown,
        highlightItemUp,
        highlightItemDown,
        selectHighlightedItem,
      }"
    >
      <div
        class="
          text-sm
          flex
          focus:outline-none
          hover:text-gray-800
          dark:hover:text-gray-100
          focus:text-gray-800
          dark:focus:text-gray-100
          items-center
          py-1
          rounded-md
          leading-relaxed
          cursor-pointer
        "
        :class="
          !value
            ? 'text-gray-600 dark:text-gray-500'
            : 'text-gray-900 dark:text-gray-300'
        "
        tabindex="0"
        @click="toggleDropdown()"
        @keydown.down="highlightItemDown"
        @keydown.up="highlightItemUp"
        @keydown.enter="selectHighlightedItem"
      >
        {{ periodSelectorMap?.[value] ?? value }}
        <feather-icon name="chevron-down" class="ms-1 w-3 h-3" />
      </div>
    </template>
  </Dropdown>
</template>

<script>
import Dropdown from './Dropdown.vue';

export default {
  name: 'PeriodSelector',
  components: {
    Dropdown,
  },
  props: {
    value: { type: String, default: 'This Year' },
    options: {
      type: Array,
      default: () => ['This Year', 'This Quarter', 'This Month', 'YTD'],
    },
  },
  emits: ['change'],
  data() {
    return {
      periodSelectorMap: {},
      periodOptions: [],
    };
  },
  mounted() {
    this.periodSelectorMap = {
      '': 'Set Period',
      'This Year': 'This Year',
      YTD: 'Year to Date',
      'This Quarter': 'This Quarter',
      'This Month': 'This Month',
    };

    this.periodOptions = this.options.map((option) => {
      let label = this.periodSelectorMap[option] ?? option;

      return {
        label,
        action: () => this.selectOption(option),
      };
    });
  },
  methods: {
    selectOption(value) {
      this.$emit('change', value);
      this.$refs.dropdown.toggleDropdown(false);
    },
  },
};
</script> 