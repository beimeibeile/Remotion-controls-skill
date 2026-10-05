// 动画配置类型定义

export interface Keyframe {
  time: number;        // 时间（秒）
  x?: number;           // 水平位置（像素，相对画布左上角）
  y?: number;           // 垂直位置（像素）
  scale?: number;       // 缩放比例
  opacity?: number;     // 透明度（0-1）
  rotation?: number;    // 旋转角度（度）
  easing?: EasingType;  // 缓动曲线
}

export type EasingType =
  | 'linear'
  | 'ease-in'
  | 'ease-out'
  | 'ease-in-out'
  | 'spring';

export interface Layer {
  id: string;
  image: string;        // 图片路径（相对于public目录）
  keyframes: Keyframe[];
  width?: number;       // 图片原始宽度（用于缩放计算）
  height?: number;      // 图片原始高度
}

export interface AnimationConfig {
  composition?: string;
  fps?: number;
  width?: number;
  height?: number;
  duration?: number;    // 总时长（秒）
  layers: Layer[];
  variables?: Record<string, any>;
}
