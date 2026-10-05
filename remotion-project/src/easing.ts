// 缓动函数
import type { EasingType } from './types';

export function easeLinear(t: number): number {
  return t;
}

export function easeInQuad(t: number): number {
  return t * t;
}

export function easeOutQuad(t: number): number {
  return t * (2 - t);
}

export function easeInOutQuad(t: number): number {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}

export function easeOutElastic(t: number): number {
  const c4 = (2 * Math.PI) / 3;
  return t === 0
    ? 0
    : t === 1
    ? 1
    : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
}

export function getEasing(type: EasingType = 'ease-out'): (t: number) => number {
  switch (type) {
    case 'linear':
      return easeLinear;
    case 'ease-in':
      return easeInQuad;
    case 'ease-out':
      return easeOutQuad;
    case 'ease-in-out':
      return easeInOutQuad;
    case 'spring':
      return easeOutElastic;
    default:
      return easeOutQuad;
  }
}

// 在两个关键帧之间插值
export function interpolate(
  currentTime: number,
  keyframes: { time: number; value?: number }[],
  property: string,
  defaultEasing: EasingType = 'ease-out',
): number {
  // 过滤出有该属性的关键帧
  const relevant = keyframes
    .filter(kf => (kf as any)[property] !== undefined)
    .sort((a, b) => a.time - b.time);

  if (relevant.length === 0) {
    return 0;
  }

  // 时间早于第一个关键帧
  if (currentTime <= relevant[0].time) {
    return (relevant[0] as any)[property];
  }

  // 时间晚于最后一个关键帧
  if (currentTime >= relevant[relevant.length - 1].time) {
    return (relevant[relevant.length - 1] as any)[property];
  }

  // 找到前后两个关键帧
  for (let i = 0; i < relevant.length - 1; i++) {
    const prev = relevant[i];
    const next = relevant[i + 1];
    if (currentTime >= prev.time && currentTime <= next.time) {
      const duration = next.time - prev.time;
      const progress = duration > 0 ? (currentTime - prev.time) / duration : 0;
      const easing = getEasing((next as any).easing || defaultEasing);
      const easedProgress = easing(progress);
      const prevValue = (prev as any)[property];
      const nextValue = (next as any)[property];
      return prevValue + (nextValue - prevValue) * easedProgress;
    }
  }

  return (relevant[relevant.length - 1] as any)[property];
}
