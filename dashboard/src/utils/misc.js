import { DateTime } from 'luxon';

export function getDatesAndPeriodList(period) {
  const toDate = DateTime.now().plus({ days: 1 });
  let fromDate;

  if (period === 'This Year') {
    fromDate = toDate.minus({ months: 12 });
  } else if (period === 'YTD') {
    fromDate = DateTime.now().startOf('year');
  } else if (period === 'This Quarter') {
    fromDate = toDate.minus({ months: 3 });
  } else if (period === 'This Month') {
    fromDate = toDate.startOf('month');
  } else {
    fromDate = toDate.minus({ days: 1 });
  }

  /**
   * periodList: Monthly decrements before toDate until fromDate
   */
  const periodList = [toDate];
  while (true) {
    const nextDate = periodList.at(0).minus({ months: 1 });
    if (nextDate.toMillis() < fromDate.toMillis()) {
      if (period === 'YTD') {
        periodList.unshift(nextDate);
        break;
      }
      break;
    }

    periodList.unshift(nextDate);
  }
  periodList.shift();

  return {
    periodList,
    fromDate,
    toDate,
  };
}

export function getValueMapFromList(list, key, value) {
  const map = {};
  for (const item of list) {
    map[item[key]] = item[value];
  }
  return map;
}

export function getIsMac() {
  return navigator.userAgent.indexOf('Mac') !== -1;
} 