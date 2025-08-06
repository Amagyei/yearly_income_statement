export const uicolors = {
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  blue: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  pink: {
    50: '#fdf2f8',
    100: '#fce7f3',
    200: '#fbcfe8',
    300: '#f9a8d4',
    400: '#f472b6',
    500: '#ec4899',
    600: '#db2777',
    700: '#be185d',
    800: '#9d174d',
    900: '#831843',
  },
};

export const indicators = {
  GRAY: 'grey',
  GREY: 'grey',
  BLUE: 'blue',
  RED: 'red',
  GREEN: 'green',
  ORANGE: 'orange',
  PURPLE: 'purple',
  YELLOW: 'yellow',
  BLACK: 'black',
};

const getValidColor = (color) => {
  const isValid = [
    'gray',
    'orange',
    'green',
    'red',
    'yellow',
    'blue',
    'indigo',
    'pink',
    'purple',
    'teal',
  ].includes(color);
  return isValid ? color : 'gray';
};

export function getBgColorClass(color) {
  const vcolor = getValidColor(color);
  return `bg-${vcolor}-200 dark:bg-${vcolor}-800`;
}

export function getColorClass(color, type = 'bg', value = 300, darkvalue = 600) {
  return `${type}-${getValidColor(color)}-${value} dark:${type}-${getValidColor(
    color
  )}-${darkvalue}`;
}

export function getTextColorClass(color) {
  return `text-${getValidColor(color)}-700 dark:text-${getValidColor(
    color
  )}-200`;
}

export function getBgTextColorClass(color) {
  const bg = getBgColorClass(color);
  const text = getTextColorClass(color);
  return [bg, text].join(' ');
} 