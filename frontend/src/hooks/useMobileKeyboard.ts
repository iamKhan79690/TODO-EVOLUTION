'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface KeyboardState {
  isKeyboardVisible: boolean;
  keyboardHeight: number;
  viewportHeight: number;
}

interface UseMobileKeyboardReturn extends KeyboardState {
  activeElement: HTMLElement | null;
  isInputFocused: boolean;
  dismissKeyboard: () => void;
  focusNextInput: () => void;
  focusPreviousInput: () => void;
}

export function useMobileKeyboard(): UseMobileKeyboardReturn {
  const [keyboardState, setKeyboardState] = useState<KeyboardState>({
    isKeyboardVisible: false,
    keyboardHeight: 0,
    viewportHeight: typeof window !== 'undefined' ? window.innerHeight : 0
  });
  const [activeElement, setActiveElement] = useState<HTMLElement | null>(null);
  const [isInputFocused, setIsInputFocused] = useState(false);

  const initialViewportHeight = useRef<number>(
    typeof window !== 'undefined' ? window.innerHeight : 0
  );
  const inputElementsRef = useRef<HTMLElement[]>([]);

  const dismissKeyboard = useCallback(() => {
    if (activeElement && 'blur' in activeElement) {
      (activeElement as HTMLElement).blur();
    }
    document.activeElement && 'blur' in document.activeElement &&
      (document.activeElement as HTMLElement).blur();
  }, [activeElement]);

  const focusNextInput = useCallback(() => {
    const inputs = Array.from(document.querySelectorAll(
      'input, textarea, [contenteditable="true"]'
    )) as HTMLElement[];

    const currentIndex = inputs.indexOf(document.activeElement as HTMLElement);
    if (currentIndex >= 0 && currentIndex < inputs.length - 1) {
      inputs[currentIndex + 1].focus();
    }
  }, []);

  const focusPreviousInput = useCallback(() => {
    const inputs = Array.from(document.querySelectorAll(
      'input, textarea, [contenteditable="true"]'
    )) as HTMLElement[];

    const currentIndex = inputs.indexOf(document.activeElement as HTMLElement);
    if (currentIndex > 0) {
      inputs[currentIndex - 1].focus();
    }
  }, []);

  useEffect(() => {
    // Set initial viewport height
    initialViewportHeight.current = window.innerHeight;

    const handleFocusIn = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      setActiveElement(target);
      setIsInputFocused(true);

      // Add input to ref array if it's not already there
      if (target.matches('input, textarea, [contenteditable="true"]')) {
        if (!inputElementsRef.current.includes(target)) {
          inputElementsRef.current.push(target);
        }
      }
    };

    const handleFocusOut = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      setActiveElement(null);
      setIsInputFocused(false);

      // Remove from ref array
      const index = inputElementsRef.current.indexOf(target);
      if (index > -1) {
        inputElementsRef.current.splice(index, 1);
      }
    };

    const handleResize = () => {
      if (!window.visualViewport) return;

      const currentHeight = window.visualViewport.height;
      const heightDifference = initialViewportHeight.current - currentHeight;

      setKeyboardState(prev => ({
        ...prev,
        viewportHeight: currentHeight,
        isKeyboardVisible: heightDifference > 150,
        keyboardHeight: heightDifference > 150 ? heightDifference : 0
      }));
    };

    const handleVisualViewportResize = () => {
      if (!window.visualViewport) return;

      const viewport = window.visualViewport;
      const heightDifference = initialViewportHeight.current - viewport.height;

      setKeyboardState({
        isKeyboardVisible: heightDifference > 150,
        keyboardHeight: heightDifference > 150 ? heightDifference : 0,
        viewportHeight: viewport.height
      });
    };

    const handleOrientationChange = () => {
      setTimeout(() => {
        initialViewportHeight.current = window.innerHeight;
        setKeyboardState({
          isKeyboardVisible: false,
          keyboardHeight: 0,
          viewportHeight: window.innerHeight
        });
      }, 100);
    };

    // Event listeners
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleVisualViewportResize);
    } else {
      window.addEventListener('resize', handleResize);
    }

    window.addEventListener('orientationchange', handleOrientationChange);

    // Handle Android-specific keyboard behavior
    const handleAndroidKeyboard = () => {
      if (/Android/i.test(navigator.userAgent)) {
        const originalHeight = initialViewportHeight.current;
        const currentHeight = window.innerHeight;

        if (currentHeight < originalHeight * 0.8) {
          setKeyboardState({
            isKeyboardVisible: true,
            keyboardHeight: originalHeight - currentHeight,
            viewportHeight: currentHeight
          });
        } else {
          setKeyboardState({
            isKeyboardVisible: false,
            keyboardHeight: 0,
            viewportHeight: currentHeight
          });
        }
      }
    };

    window.addEventListener('resize', handleAndroidKeyboard);

    return () => {
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);

      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleVisualViewportResize);
      } else {
        window.removeEventListener('resize', handleResize);
      }

      window.removeEventListener('orientationchange', handleOrientationChange);
      window.removeEventListener('resize', handleAndroidKeyboard);
    };
  }, []);

  return {
    ...keyboardState,
    activeElement,
    isInputFocused,
    dismissKeyboard,
    focusNextInput,
    focusPreviousInput
  };
}

// Hook for keyboard-aware scrolling
export function useKeyboardAwareScroll(dependencies: any[] = []) {
  const { keyboardHeight, isKeyboardVisible } = useMobileKeyboard();
  const scrollTargetRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isKeyboardVisible && scrollTargetRef.current) {
      // Scroll the target element into view with padding
      setTimeout(() => {
        scrollTargetRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest'
        });
      }, 300); // Wait for keyboard animation
    }
  }, [keyboardHeight, isKeyboardVisible, ...dependencies]);

  const setScrollTarget = useCallback((element: HTMLElement | null) => {
    scrollTargetRef.current = element;
  }, []);

  return {
    setScrollTarget,
    keyboardHeight,
    isKeyboardVisible
  };
}

// Hook for preventing zoom on input focus (common mobile issue)
export function usePreventInputZoom() {
  useEffect(() => {
    const handleFocus = (e: FocusEvent) => {
      const target = e.target as HTMLInputElement | HTMLTextAreaElement;
      if (target && (target.type === 'text' || target.type === 'email' || target.type === 'password' || target.tagName === 'TEXTAREA')) {
        // Prevent zoom by adjusting font size
        const originalFontSize = window.getComputedStyle(target).fontSize;
        target.style.fontSize = '16px';

        const handleBlur = () => {
          target.style.fontSize = originalFontSize;
          target.removeEventListener('blur', handleBlur);
        };

        target.addEventListener('blur', handleBlur);
      }
    };

    document.addEventListener('focus', handleFocus, true);

    return () => {
      document.removeEventListener('focus', handleFocus, true);
    };
  }, []);
}

// Hook for safe area insets (notch and home indicator)
export function useSafeAreaInsets() {
  const [insets, setInsets] = useState({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  });

  useEffect(() => {
    const updateInsets = () => {
      const computedStyle = getComputedStyle(document.documentElement);
      const top = parseInt(computedStyle.getPropertyValue('safe-area-inset-top') || '0');
      const right = parseInt(computedStyle.getPropertyValue('safe-area-inset-right') || '0');
      const bottom = parseInt(computedStyle.getPropertyValue('safe-area-inset-bottom') || '0');
      const left = parseInt(computedStyle.getPropertyValue('safe-area-inset-left') || '0');

      setInsets({ top, right, bottom, left });
    };

    updateInsets();

    // Listen for orientation changes
    window.addEventListener('orientationchange', updateInsets);
    window.addEventListener('resize', updateInsets);

    return () => {
      window.removeEventListener('orientationchange', updateInsets);
      window.removeEventListener('resize', updateInsets);
    };
  }, []);

  return insets;
}

// Utility function to detect if device is mobile
export function isMobileDevice(): boolean {
  if (typeof window === 'undefined') return false;

  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  ) || window.innerWidth <= 768;
}

// Utility function to get mobile-specific styles
export function getMobileStyles(keyboardHeight: number) {
  return {
    paddingBottom: isMobileDevice() ? `${Math.max(20, keyboardHeight / 4)}px` : '20px',
    minHeight: isMobileDevice() ? `calc(100vh - ${keyboardHeight}px)` : '100vh',
    transition: 'all 0.3s ease-out'
  };
}