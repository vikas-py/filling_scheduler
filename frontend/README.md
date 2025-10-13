# Filling Scheduler Frontend# React + TypeScript + Vite



Modern React + Vite + TypeScript frontend for the Filling Scheduler application.This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.



## 🚀 Quick StartCurrently, two official plugins are available:



### Prerequisites- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh

- Node.js 18+ installed- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

- Backend API running on `http://localhost:8000`

## React Compiler

### Installation

```bashThe React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

npm install

```## Expanding the ESLint configuration



### DevelopmentIf you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```bash

npm run dev```js

# Opens http://localhost:5173export default defineConfig([

```  globalIgnores(['dist']),

  {

### Build    files: ['**/*.{ts,tsx}'],

```bash    extends: [

npm run build          # Build for production      // Other configs...

npm run preview        # Preview production build

```      // Remove tseslint.configs.recommended and replace with this

      tseslint.configs.recommendedTypeChecked,

### Testing      // Alternatively, use this for stricter rules

```bash      tseslint.configs.strictTypeChecked,

npm run test           # Run tests      // Optionally, add this for stylistic rules

npm run test:ui        # Open Vitest UI      tseslint.configs.stylisticTypeChecked,

npm run coverage       # Generate coverage report

```      // Other configs...

    ],

### Linting & Formatting    languageOptions: {

```bash      parserOptions: {

npm run lint           # Run ESLint        project: ['./tsconfig.node.json', './tsconfig.app.json'],

npm run format         # Run Prettier        tsconfigRootDir: import.meta.dirname,

```      },

      // other options...

---    },

  },

## 📁 Project Structure])

```

```

src/You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

├── api/              # API clients (auth, schedules, config)

├── components/       # React components```js

│   ├── common/       # Shared components (buttons, cards, modals)// eslint.config.js

│   ├── layout/       # App layout (navbar, sidebar, footer)import reactX from 'eslint-plugin-react-x'

│   ├── schedule/     # Schedule-specific componentsimport reactDom from 'eslint-plugin-react-dom'

│   ├── compare/      # Comparison components

│   ├── config/       # Configuration componentsexport default defineConfig([

│   └── upload/       # File upload components  globalIgnores(['dist']),

├── pages/            # Page components (routes)  {

├── hooks/            # Custom React hooks    files: ['**/*.{ts,tsx}'],

├── store/            # Zustand state management    extends: [

├── types/            # TypeScript type definitions      // Other configs...

├── utils/            # Utility functions      // Enable lint rules for React

│   ├── constants.ts  # API endpoints, routes, enums      reactX.configs['recommended-typescript'],

│   ├── formatters.ts # Date, number, string formatters      // Enable lint rules for React DOM

│   └── validators.ts # Form and data validation      reactDom.configs.recommended,

├── App.tsx           # Root component    ],

├── main.tsx          # Entry point    languageOptions: {

└── router.tsx        # React Router configuration      parserOptions: {

```        project: ['./tsconfig.node.json', './tsconfig.app.json'],

        tsconfigRootDir: import.meta.dirname,

---      },

      // other options...

## 🛠️ Tech Stack    },

  },

### Core])

- **React 18**: UI library with concurrent features```

- **Vite**: Fast build tool and dev server
- **TypeScript**: Static type checking
- **Material-UI (MUI)**: Component library

### State Management
- **Zustand**: Lightweight state management
- **React Query**: Data fetching and caching

### Forms & Validation
- **React Hook Form**: Performant form handling
- **Zod**: TypeScript-first schema validation

### Data Visualization
- **Recharts**: Chart library
- **React Gantt Timeline**: Gantt chart component

### Real-time
- **Socket.io Client**: WebSocket connections

### Testing
- **Vitest**: Fast unit testing
- **React Testing Library**: Component testing
- **@testing-library/user-event**: User interaction testing

---

## 🔧 Configuration

### Environment Variables

Create `.env.development` for local development:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Create `.env.production` for production:
```env
VITE_API_URL=https://api.fillscheduler.example.com
VITE_WS_URL=wss://api.fillscheduler.example.com
```

### API Proxy

In development, API calls to `/api/*` are proxied to `http://localhost:8000` (configured in `vite.config.ts`).

### Path Aliases

Use `@/` for clean imports:
```typescript
import { Button } from '@/components/common/Button'
import { useAuth } from '@/hooks/useAuth'
import type { Schedule } from '@/types'
```

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.3 | UI library |
| @mui/material | ^6.3 | Component library |
| zustand | ^5.0 | State management |
| axios | ^1.7 | HTTP client |
| @tanstack/react-query | ^5.64 | Data fetching |
| react-hook-form | ^7.54 | Form handling |
| zod | ^3.24 | Validation |
| recharts | ^2.15 | Charts |
| socket.io-client | ^4.8 | WebSocket |
| react-dropzone | ^14.3 | File upload |
| date-fns | ^4.1 | Date utilities |

---

## 🧪 Testing

### Run Tests
```bash
npm run test
```

### Coverage Report
```bash
npm run coverage
```

### Test Files Location
- Unit tests: `src/**/*.test.ts(x)`
- Integration tests: `src/**/*.integration.test.ts(x)`
- Test utilities: `src/test/`

---

## 📝 Development Workflow

1. **Create Branch**: `git checkout -b feature/your-feature`
2. **Make Changes**: Edit files in `src/`
3. **Run Tests**: `npm run test`
4. **Lint**: `npm run lint`
5. **Format**: `npm run format`
6. **Commit**: `git commit -m "feat: your feature"`
7. **Push**: `git push origin feature/your-feature`

---

## 🎨 Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: TypeScript + React rules
- **Prettier**: Consistent formatting
- **Line Length**: 100 characters
- **Quotes**: Single quotes
- **Semicolons**: No semicolons
- **Indentation**: 2 spaces

---

## 🔗 Related Documentation

- **API Guide**: [docs/API_GUIDE.md](../docs/API_GUIDE.md)
- **Postman Collection**: [postman/README.md](../postman/README.md)
- **Phase 2.1 Summary**: [docs/PHASE_2.1_COMPLETION_SUMMARY.md](../docs/PHASE_2.1_COMPLETION_SUMMARY.md)
- **Progress Tracker**: [docs/PHASE_2_PROGRESS.md](../docs/PHASE_2_PROGRESS.md)

---

## 📊 Project Status

- **Phase 2.1**: ✅ Complete (Project Setup)
- **Phase 2.2**: 🚧 Next (Authentication & Layout)
- **Overall Progress**: 7% (4/59 tasks)

---

## 🤝 Contributing

1. Follow the TypeScript style guide
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
5. Format code with Prettier

---

## 📄 License

MIT
