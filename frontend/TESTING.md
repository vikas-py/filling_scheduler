# Testing Guide

This document explains the testing setup and how to run tests for the Filling Scheduler frontend.

## Test Framework

- **Vitest** - Fast unit test framework (Vite-native)
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom matchers for DOM assertions

## Running Tests

```bash
# Run tests in watch mode (interactive)
npm test

# Run tests once (CI mode)
npm run test:run

# Run tests with UI (visual test runner)
npm run test:ui

# Run tests with coverage report
npm run test:coverage
```

## Test Structure

```
src/
├── components/
│   └── common/
│       └── __tests__/
│           ├── EmptyState.test.tsx
│           ├── LoadingButton.test.tsx
│           └── ConnectionStatus.test.tsx
├── pages/
│   └── __tests__/
│       └── Dashboard.test.tsx
├── api/
│   └── __tests__/
│       └── schedules.test.ts
└── test/
    ├── setup.ts           # Test environment setup
    ├── test-utils.tsx     # Custom render functions
    └── mocks.ts           # Mock data
```

## Writing Tests

### Component Tests

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### API Tests

```typescript
import { describe, it, expect } from 'vitest';
import { mockSchedule } from '@/test/mocks';

describe('API', () => {
  it('validates data structure', () => {
    expect(mockSchedule).toHaveProperty('id');
    expect(mockSchedule).toHaveProperty('name');
  });
});
```

## Test Utilities

### Custom Render

The `renderWithProviders` function wraps components with necessary providers:

```typescript
import { render } from '@/test/test-utils';

render(<MyComponent />);
// Automatically wrapped with:
// - QueryClientProvider
// - ThemeProvider
// - BrowserRouter
```

### Mock Data

Use predefined mocks from `@/test/mocks`:

```typescript
import { mockSchedule, mockSchedules, mockUser } from '@/test/mocks';
```

## Coverage Reports

After running `npm run test:coverage`, view the HTML report:

```bash
# Open in browser
open coverage/index.html  # Mac
start coverage/index.html # Windows
xdg-open coverage/index.html # Linux
```

## Coverage Thresholds

Minimum coverage requirements (configured in `vitest.config.ts`):

- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 70%
- **Statements**: 70%

## Current Test Coverage

### Components (6 tests)

- ✅ EmptyState (6 tests)
- ✅ LoadingButton (6 tests)
- ✅ ConnectionStatus (5 tests)

### Pages (3 tests)

- ✅ Dashboard (3 tests)

### API (6 tests)

- ✅ Schedule types (6 tests)

**Total**: 20 tests

## Best Practices

### 1. Test User Behavior

```typescript
// Good: Test what users see
expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();

// Avoid: Testing implementation details
expect(wrapper.find('.submit-btn')).toHaveLength(1);
```

### 2. Use Semantic Queries

Priority order:
1. `getByRole` - Best for accessibility
2. `getByLabelText` - Form fields
3. `getByPlaceholderText` - Inputs
4. `getByText` - General content
5. `getByTestId` - Last resort

### 3. Async Tests

```typescript
import { waitFor } from '@testing-library/react';

it('loads data', async () => {
  render(<MyComponent />);

  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeInTheDocument();
  });
});
```

### 4. User Events

```typescript
import { userEvent } from '@testing-library/user-event';

it('handles click', async () => {
  const user = userEvent.setup();
  render(<Button>Click</Button>);

  await user.click(screen.getByRole('button'));
});
```

## Troubleshooting

### Tests Won't Run

```bash
# Clear cache
rm -rf node_modules/.vite

# Reinstall
npm install
```

### Import Errors

Check that path aliases are configured in both:
- `vite.config.ts`
- `vitest.config.ts`

### Timeout Errors

Increase test timeout in `vitest.config.ts`:

```typescript
test: {
  testTimeout: 10000, // 10 seconds
}
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run tests
  run: npm run test:run

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
```

## Future Tests

### E2E Tests (Phase 2.9 - Not Yet Implemented)

Will use Playwright for end-to-end testing:

```bash
# Install Playwright (future)
npm install -D @playwright/test

# Run E2E tests (future)
npx playwright test
```

### Accessibility Tests (Phase 2.9 - Not Yet Implemented)

Will integrate axe-core:

```bash
# Install axe (future)
npm install -D @axe-core/react

# Run a11y tests (future)
npm run test:a11y
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Last Updated**: January 14, 2025
