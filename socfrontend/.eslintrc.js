module.exports = {
  env: {
    browser: true,
    es2021: true,
    jest: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: ['react', 'react-hooks'],
  rules: {
    'max-len': ['warn', {
      code: 120,
      ignoreUrls: true,
      ignoreStrings: true,
      ignoreTemplateLiterals: true,
      ignoreRegExpLiterals: true
    }],
    'no-console': 'warn',
    'react/prop-types': 'off', // Disabled prop-types validation for now
    'react/react-in-jsx-scope': 'off',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-unused-vars': ['warn', {
      "vars": "all",
      "args": "after-used",
      "ignoreRestSiblings": true
    }],
    'react/no-unescaped-entities': 'off',
    'no-undef': 'error',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  globals: {
    process: 'readonly',
  },
} 