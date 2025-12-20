'use client';

import { useEffect, useState } from 'react';

// Breakpoint definitions
export const BREAKPOINTS = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
} as const;

export type Breakpoint = keyof typeof BREAKPOINTS;

// Device detection utilities
export const isMobileDevice = () => {
  if (typeof window === 'undefined') return false;

  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  ) || window.innerWidth <= BREAKPOINTS.md;
};

export const isTabletDevice = () => {
  if (typeof window === 'undefined') return false;

  return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent) ||
         (window.innerWidth > BREAKPOINTS.md && window.innerWidth <= BREAKPOINTS.lg);
};

export const isDesktopDevice = () => {
  if (typeof window === 'undefined') return false;

  return window.innerWidth > BREAKPOINTS.lg && !isTabletDevice();
};

// Touch capability detection
export const isTouchDevice = () => {
  if (typeof window === 'undefined') return false;

  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    // @ts-ignore
    navigator.msMaxTouchPoints > 0
  );
};

// Screen orientation utilities
export const getOrientation = () => {
  if (typeof window === 'undefined') return 'portrait';

  return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
};

export const isPortrait = () => getOrientation() === 'portrait';
export const isLandscape = () => getOrientation() === 'landscape';

// Responsive hook
export function useResponsive() {
  const [screenSize, setScreenSize] = useState(() => ({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768
  }));

  const [breakpoint, setBreakpoint] = useState<Breakpoint>(() => {
    if (typeof window === 'undefined') return 'lg';

    const width = window.innerWidth;
    if (width <= BREAKPOINTS.sm) return 'sm';
    if (width <= BREAKPOINTS.md) return 'md';
    if (width <= BREAKPOINTS.lg) return 'lg';
    if (width <= BREAKPOINTS.xl) return 'xl';
    return '2xl';
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      setScreenSize({ width, height });

      // Determine current breakpoint
      let currentBreakpoint: Breakpoint = '2xl';
      for (const [key, value] of Object.entries(BREAKPOINTS)) {
        if (width <= value) {
          currentBreakpoint = key as Breakpoint;
          break;
        }
      }
      setBreakpoint(currentBreakpoint);
    };

    handleResize();

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return {
    screenSize,
    breakpoint,
    isMobile: screenSize.width <= BREAKPOINTS.md,
    isTablet: screenSize.width > BREAKPOINTS.md && screenSize.width <= BREAKPOINTS.lg,
    isDesktop: screenSize.width > BREAKPOINTS.lg,
    isTouch: isTouchDevice(),
    orientation: getOrientation(),
    isPortrait: isPortrait(),
    isLandscape: isLandscape()
  };
}

// Responsive utility classes generator
export const getResponsiveClasses = (config: {
  base?: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  '2xl'?: string;
}) => {
  const classes = [config.base || ''];

  Object.entries(config).forEach(([key, value]) => {
    if (key !== 'base' && value) {
      if (key === breakpointToString(useResponsive().breakpoint)) {
        classes.push(value);
      } else {
        classes.push(`${key}:${value}`);
      }
    }
  });

  return classes.filter(Boolean).join(' ');
};

function breakpointToString(breakpoint: Breakpoint): string {
  return breakpoint;
}

// Touch-friendly sizing utilities
export const getTouchTargetSize = (size: 'small' | 'medium' | 'large' = 'medium') => {
  const sizes = {
    small: { min: 44, padding: 8 },
    medium: { min: 48, padding: 12 },
    large: { min: 56, padding: 16 }
  };

  return sizes[size];
};

// Safe area utilities
export const getSafeAreaInsets = () => {
  if (typeof window === 'undefined') return { top: 0, right: 0, bottom: 0, left: 0 };

  const computedStyle = getComputedStyle(document.documentElement);
  return {
    top: parseInt(computedStyle.getPropertyValue('safe-area-inset-top') || '0'),
    right: parseInt(computedStyle.getPropertyValue('safe-area-inset-right') || '0'),
    bottom: parseInt(computedStyle.getPropertyValue('safe-area-inset-bottom') || '0'),
    left: parseInt(computedStyle.getPropertyValue('safe-area-inset-left') || '0')
  };
};

// Mobile viewport utilities
export const getMobileViewportHeight = () => {
  if (typeof window === 'undefined') return window.innerHeight || 768;

  return window.visualViewport?.height || window.innerHeight;
};

export const getVisualViewport = () => {
  if (typeof window === 'undefined') return null;

  return window.visualViewport || {
    height: window.innerHeight,
    width: window.innerWidth,
    offsetLeft: 0,
    offsetTop: 0,
    scale: 1
  };
};

// Keyboard utilities
export const getKeyboardHeight = () => {
  if (typeof window === 'undefined') return 0;

  const visualViewport = getVisualViewport();
  if (!visualViewport) return 0;

  return Math.max(0, window.innerHeight - visualViewport.height);
};

export const isKeyboardVisible = () => {
  return getKeyboardHeight() > 150;
};

// Performance utilities for mobile
export const shouldUseReducedMotion = () => {
  if (typeof window === 'undefined') return false;

  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

export const shouldUseHover = () => {
  if (typeof window === 'undefined') return true;

  return window.matchMedia('(hover: hover)').matches && !isTouchDevice();
};

// Device-specific optimizations
export const getDeviceOptimizations = () => {
  const isMobile = isMobileDevice();
  const isTouch = isTouchDevice();
  const prefersReducedMotion = shouldUseReducedMotion();
  const canHover = shouldUseHover();

  return {
    // Animation settings
    animationDuration: prefersReducedMotion ? '0ms' : isMobile ? '200ms' : '300ms',
    animationEasing: prefersReducedMotion ? 'none' : 'cubic-bezier(0.4, 0, 0.2, 1)',

    // Touch settings
    touchAction: isTouch ? 'manipulation' : 'auto',
    userSelect: isMobile ? 'none' : 'auto',

    // Hover settings
    hoverEffects: canHover && !isTouch,

    // Layout settings
    maxContentWidth: isMobile ? '100vw' : '1200px',
    spacingUnit: isMobile ? '4px' : '8px',

    // Performance settings
    willChange: prefersReducedMotion ? 'auto' : 'transform, opacity',
    transform: prefersReducedMotion ? 'none' : 'translateZ(0)', // Hardware acceleration
  };
};

// Mobile-specific CSS utilities
export const getMobileStyles = (keyboardHeight: number = 0) => {
  const isMobile = isMobileDevice();
  const safeInsets = getSafeAreaInsets();

  return {
    // Layout adjustments
    minHeight: isMobile ? '100vh' : 'auto',
    paddingBottom: isMobile
      ? `max(${safeInsets.bottom}px, ${Math.max(20, keyboardHeight / 4)}px)`
      : '20px',

    // Touch-friendly sizing
    minHeightTouch: isMobile ? '44px' : '32px',
    minWidthTouch: isMobile ? '44px' : '32px',

    // Mobile spacing
    mobilePadding: isMobile ? '16px' : '24px',
    mobileMargin: isMobile ? '8px' : '16px',

    // Mobile font sizes
    mobileTextSm: isMobile ? '14px' : '12px',
    mobileTextBase: isMobile ? '16px' : '14px',
    mobileTextLg: isMobile ? '18px' : '16px',

    // Mobile border radius
    mobileRadius: isMobile ? '12px' : '8px',

    // Mobile shadows
    mobileShadow: isMobile
      ? '0 2px 8px rgba(0, 0, 0, 0.1)'
      : '0 4px 12px rgba(0, 0, 0, 0.15)',
  };
};

// Responsive image utilities
export const getResponsiveImageProps = (baseSrc: string, options: {
  sizes?: string[];
  formats?: ('webp' | 'avif' | 'jpg' | 'png')[];
  quality?: number;
} = {}) => {
  const { sizes = [400, 800, 1200], formats = ['webp', 'jpg'], quality = 80 } = options;

  const srcSet = sizes
    .map(size => `${baseSrc}?w=${size}&q=${quality} ${size}w`)
    .join(', ');

  return {
    srcSet,
    sizes: '(max-width: 640px) 400px, (max-width: 1024px) 800px, 1200px',
    loading: 'lazy' as const,
    decoding: 'async' as const,
  };
};

// Mobile gesture utilities
export const getGestureConfig = () => {
  return {
    swipeThreshold: isMobileDevice() ? 50 : 100,
    swipeVelocity: isMobileDevice() ? 0.3 : 0.5,
    tapThreshold: 10,
    longPressDelay: 500,
    doubleTapDelay: 300,
  };
};

// Export all utilities for easy importing
export const mobileUtils = {
  // Device detection
  isMobileDevice,
  isTabletDevice,
  isDesktopDevice,
  isTouchDevice,

  // Responsive
  useResponsive,
  getResponsiveClasses,

  // Touch and sizing
  getTouchTargetSize,
  getMobileStyles,

  // Viewport and keyboard
  getMobileViewportHeight,
  getVisualViewport,
  getKeyboardHeight,
  isKeyboardVisible,

  // Safe area
  getSafeAreaInsets,

  // Performance
  shouldUseReducedMotion,
  shouldUseHover,
  getDeviceOptimizations,

  // Media
  getResponsiveImageProps,

  // Gestures
  getGestureConfig,
};