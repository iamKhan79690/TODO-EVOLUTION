import { ValidationError, ValidationRules } from '@/lib/chat-types';

/**
 * Input validation utilities for ChatKit frontend
 * Provides comprehensive validation with type safety and error messages
 */

// Validation rules as constants
export const VALIDATION_RULES: ValidationRules = {
  message: {
    minLength: 1,
    maxLength: 10000,
    allowedCharacters: /^[\s\S]*$/, // Any characters including spaces and newlines
  },
  conversation: {
    title: {
      minLength: 1,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9\s\-_.,!?]+$/,
    },
  },
  preferences: {
    pollingInterval: {
      min: 1000,
      max: 10000,
      step: 500,
    },
  },
};

// Common validation patterns
export const PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  url: /^https?:\/\/.+/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  name: /^[a-zA-Z\s\-'.]+$/,
  safeString: /^[a-zA-Z0-9\s\-_.,!?@#%&*()+=\[\]{}|;:'"<>?/\\]+$/,
} as const;

// Validation error codes
export const ERROR_CODES = {
  REQUIRED: 'REQUIRED',
  TOO_SHORT: 'TOO_SHORT',
  TOO_LONG: 'TOO_LONG',
  INVALID_FORMAT: 'INVALID_FORMAT',
  INVALID_EMAIL: 'INVALID_EMAIL',
  INVALID_URL: 'INVALID_URL',
  OUT_OF_RANGE: 'OUT_OF_RANGE',
  CONTAINS_PROFANITY: 'CONTAINS_PROFANITY',
  INVALID_CHARACTERS: 'INVALID_CHARACTERS',
} as const;

/**
 * Validate a single field against rules
 */
export function validateField(
  value: string,
  rules: {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    min?: number;
    max?: number;
    custom?: (value: string) => string | null;
  }
): ValidationError | null {
  // Check if required and empty
  if (rules.required && (!value || value.trim().length === 0)) {
    return {
      field: '',
      message: 'This field is required',
      code: ERROR_CODES.REQUIRED,
    };
  }

  // Skip other validations if field is not required and empty
  if (!value || value.trim().length === 0) {
    return null;
  }

  const trimmedValue = value.trim();

  // Length validation
  if (rules.minLength && trimmedValue.length < rules.minLength) {
    return {
      field: '',
      message: `Must be at least ${rules.minLength} characters long`,
      code: ERROR_CODES.TOO_SHORT,
    };
  }

  if (rules.maxLength && trimmedValue.length > rules.maxLength) {
    return {
      field: '',
      message: `Must be no more than ${rules.maxLength} characters long`,
      code: ERROR_CODES.TOO_LONG,
    };
  }

  // Pattern validation
  if (rules.pattern && !rules.pattern.test(trimmedValue)) {
    return {
      field: '',
      message: 'Contains invalid characters',
      code: ERROR_CODES.INVALID_FORMAT,
    };
  }

  // Numeric range validation
  if (rules.min !== undefined && Number(trimmedValue) < rules.min) {
    return {
      field: '',
      message: `Must be at least ${rules.min}`,
      code: ERROR_CODES.OUT_OF_RANGE,
    };
  }

  if (rules.max !== undefined && Number(trimmedValue) > rules.max) {
    return {
      field: '',
      message: `Must be no more than ${rules.max}`,
      code: ERROR_CODES.OUT_OF_RANGE,
    };
  }

  // Custom validation
  if (rules.custom) {
    const customError = rules.custom(trimmedValue);
    if (customError) {
      return {
        field: '',
        message: customError,
        code: ERROR_CODES.INVALID_FORMAT,
      };
    }
  }

  return null;
}

/**
 * Validate message content
 */
export function validateMessage(content: string): ValidationError | null {
  return validateField(content, {
    required: true,
    minLength: VALIDATION_RULES.message.minLength,
    maxLength: VALIDATION_RULES.message.maxLength,
    pattern: VALIDATION_RULES.message.allowedCharacters,
    custom: (value) => {
      // Check for potential XSS attempts
      if (/<script|javascript:|on\w+=/i.test(value)) {
        return 'Contains potentially unsafe content';
      }
      return null;
    },
  });
}

/**
 * Validate conversation title
 */
export function validateConversationTitle(title: string): ValidationError | null {
  return validateField(title, {
    required: true,
    minLength: VALIDATION_RULES.conversation.title.minLength,
    maxLength: VALIDATION_RULES.conversation.title.maxLength,
    pattern: VALIDATION_RULES.conversation.title.pattern,
  });
}

/**
 * Validate email address
 */
export function validateEmail(email: string): ValidationError | null {
  return validateField(email, {
    required: true,
    pattern: PATTERNS.email,
    custom: (value) => {
      if (value.length > 254) {
        return 'Email address is too long';
      }
      return null;
    },
  });
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): ValidationError | null {
  return validateField(password, {
    required: true,
    minLength: 8,
    maxLength: 128,
    custom: (value) => {
      if (!/(?=.*[a-z])/.test(value)) {
        return 'Must contain at least one lowercase letter';
      }
      if (!/(?=.*[A-Z])/.test(value)) {
        return 'Must contain at least one uppercase letter';
      }
      if (!/(?=.*\d)/.test(value)) {
        return 'Must contain at least one number';
      }
      if (!/(?=.*[@$!%*?&])/.test(value)) {
        return 'Must contain at least one special character';
      }
      return null;
    },
  });
}

/**
 * Validate user name
 */
export function validateName(name: string): ValidationError | null {
  return validateField(name, {
    required: true,
    minLength: 2,
    maxLength: 50,
    pattern: PATTERNS.name,
  });
}

/**
 * Validate polling interval preference
 */
export function validatePollingInterval(interval: string | number): ValidationError | null {
  const value = typeof interval === 'string' ? interval : interval.toString();
  return validateField(value, {
    required: true,
    min: VALIDATION_RULES.preferences.pollingInterval.min,
    max: VALIDATION_RULES.preferences.pollingInterval.max,
    custom: (val) => {
      const num = Number(val);
      if (num % VALIDATION_RULES.preferences.pollingInterval.step !== 0) {
        return `Must be in increments of ${VALIDATION_RULES.preferences.pollingInterval.step}ms`;
      }
      return null;
    },
  });
}

/**
 * Validate theme preference
 */
export function validateTheme(theme: string): ValidationError | null {
  const validThemes = ['light', 'dark', 'system'];
  if (!validThemes.includes(theme)) {
    return {
      field: 'theme',
      message: 'Invalid theme preference',
      code: ERROR_CODES.INVALID_FORMAT,
    };
  }
  return null;
}

/**
 * Validate font size preference
 */
export function validateFontSize(fontSize: string): ValidationError | null {
  const validSizes = ['small', 'medium', 'large'];
  if (!validSizes.includes(fontSize)) {
    return {
      field: 'fontSize',
      message: 'Invalid font size preference',
      code: ERROR_CODES.INVALID_FORMAT,
    };
  }
  return null;
}

/**
 * Validate complete user preferences object
 */
export function validateUserPreferences(preferences: Record<string, any>): ValidationError[] {
  const errors: ValidationError[] = [];

  // Validate theme
  if (preferences.theme) {
    const themeError = validateTheme(preferences.theme);
    if (themeError) {
      themeError.field = 'theme';
      errors.push(themeError);
    }
  }

  // Validate font size
  if (preferences.fontSize) {
    const fontSizeError = validateFontSize(preferences.fontSize);
    if (fontSizeError) {
      fontSizeError.field = 'fontSize';
      errors.push(fontSizeError);
    }
  }

  // Validate polling interval
  if (preferences.pollingInterval !== undefined) {
    const intervalError = validatePollingInterval(preferences.pollingInterval);
    if (intervalError) {
      intervalError.field = 'pollingInterval';
      errors.push(intervalError);
    }
  }

  return errors;
}

/**
 * Sanitize user input to prevent XSS
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Check if string contains potentially unsafe content
 */
export function containsUnsafeContent(input: string): boolean {
  const unsafePatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
  ];

  return unsafePatterns.some(pattern => pattern.test(input));
}

/**
 * Truncate text to specified length with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format validation errors for display
 */
export function formatValidationErrors(errors: ValidationError[]): Record<string, string> {
  const formattedErrors: Record<string, string> = {};

  errors.forEach(error => {
    if (error.field) {
      formattedErrors[error.field] = error.message;
    }
  });

  return formattedErrors;
}

/**
 * Validate form data object with field-level validation
 */
export function validateFormData(
  data: Record<string, any>,
  validationRules: Record<string, any>
): { isValid: boolean; errors: Record<string, string> } {
  const errors: Record<string, string> = {};

  Object.entries(validationRules).forEach(([field, rules]) => {
    const validationError = validateField(data[field] || '', rules);
    if (validationError) {
      errors[field] = validationError.message;
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

export default {
  validateField,
  validateMessage,
  validateConversationTitle,
  validateEmail,
  validatePassword,
  validateName,
  validatePollingInterval,
  validateTheme,
  validateFontSize,
  validateUserPreferences,
  sanitizeInput,
  containsUnsafeContent,
  truncateText,
  formatValidationErrors,
  validateFormData,
  VALIDATION_RULES,
  PATTERNS,
  ERROR_CODES,
};