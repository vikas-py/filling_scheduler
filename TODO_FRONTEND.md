# Frontend TODO List

Comprehensive list of placeholders, TODOs, and incomplete functionalities in the frontend codebase.

Last updated: 2025-10-14

---

## 🔴 Critical Priority (Must Fix)

### 1. Schedule Management Features

#### [src/pages/ScheduleDetail.tsx:95](frontend/src/pages/ScheduleDetail.tsx#L95)
- **Issue**: `TODO: Implement delete` - Delete functionality not implemented
- **Current**: Only navigates away without actually deleting
- **Required**: Call `deleteSchedule(schedule.id)` API endpoint
- **Impact**: Users cannot delete schedules

#### [src/pages/ScheduleDetail.tsx:103](frontend/src/pages/ScheduleDetail.tsx#L103)
- **Issue**: `TODO: Implement export functionality` - Export buttons non-functional
- **Current**: Only logs to console
- **Required**: Implement download logic for:
  - CSV export of schedule data
  - JSON export of schedule data
  - PNG export of Gantt chart visualization
- **Impact**: Users cannot export schedules

### 2. Configuration Persistence

#### [src/pages/Config.tsx:32](frontend/src/pages/Config.tsx#L32)
- **Issue**: `TODO: Implement save functionality` - Config changes not saved
- **Current**: Shows success message without persisting
- **Required**:
  - Create API endpoint for saving configuration
  - Implement API call in frontend
  - Handle errors and validation
- **Impact**: Configuration changes are lost

#### [src/pages/Config.tsx:41](frontend/src/pages/Config.tsx#L41)
- **Issue**: `TODO: Implement reset functionality` - Reset button not working
- **Current**: Only logs to console
- **Required**:
  - API call to reset config or reset local state
  - Reload default values
- **Impact**: Users cannot reset to defaults

### 3. Dashboard Data Integration

#### [src/components/dashboard/DashboardKpiCards.tsx:9-14](frontend/src/components/dashboard/DashboardKpiCards.tsx#L9-L14)
- **Issue**: Using mock data with all 0 values
- **Current**: Hardcoded placeholder statistics
- **Required**:
  - Connect to existing `getScheduleStats()` API
  - Display real statistics
  - Add error handling
- **Impact**: Dashboard shows incorrect data

#### [src/components/dashboard/DashboardCharts.tsx:16-31](frontend/src/components/dashboard/DashboardCharts.tsx#L16-L31)
- **Issue**: Charts using mock data
- **Current**: Hardcoded 0 values for strategies and status distribution
- **Required**:
  - Fetch real chart data from API
  - Create API endpoint if needed
  - Update charts dynamically
- **Impact**: Dashboard charts meaningless

### 4. Missing Core Pages

#### [src/router.tsx:44](frontend/src/router.tsx#L44)
- **Issue**: Schedules list page shows "Coming Soon"
- **Current**: Placeholder text only
- **Required**:
  - Create SchedulesList component
  - Implement filtering and search
  - Connect to schedules API
  - Add pagination
- **Impact**: Users cannot view schedule list

#### [src/hooks/useKeyboardShortcuts.ts:61](frontend/src/hooks/useKeyboardShortcuts.ts#L61)
- **Issue**: Help dialog shortcut (Ctrl+/) only logs to console
- **Current**: No dialog implementation
- **Required**:
  - Create HelpDialog component
  - Implement state management
  - Show keyboard shortcuts guide
- **Impact**: Help feature non-functional

---

## 🟡 High Priority (Should Fix)

### 5. Error Handling Improvements

#### [src/pages/Dashboard.tsx:61-63](frontend/src/pages/Dashboard.tsx#L61-L63)
- **Issue**: Schedule fetch errors only log to console
- **Required**: Display error toast/alert to user
- **Files**: Multiple files with similar issues

#### [src/hooks/useWebSocket.ts](frontend/src/hooks/useWebSocket.ts)
- **Line 104-106**: Message parse errors not shown to user
- **Line 109-112**: WebSocket errors don't provide user feedback
- **Line 137-140**: Connection errors should notify user
- **Line 131**: Max reconnection attempts should alert user
- **Required**:
  - Add toast notifications for errors
  - Show connection status indicator
  - Implement reconnection UI feedback

### 6. Configuration Settings Persistence

#### [src/components/config/GeneralSettings.tsx](frontend/src/components/config/GeneralSettings.tsx)
- **Issue**: All settings (theme, language, notifications) are UI-only
- **Required**:
  - Create user preferences API
  - Save settings to backend/localStorage
  - Load settings on app initialization
  - Sync across sessions
- **Impact**: User preferences lost on refresh

#### [src/components/config/StrategyDefaults.tsx](frontend/src/components/config/StrategyDefaults.tsx)
- **Issue**: Strategy defaults not persisted
- **Required**:
  - Save custom strategy defaults
  - Apply defaults to new schedule creation
  - Add validation for strategy parameters

#### [src/components/config/FillerSettings.tsx](frontend/src/components/config/FillerSettings.tsx)
- **Issue**: Filler configs are local state only
- **Required**:
  - Persist to backend
  - Load from API on mount
  - Validate capacity vs concurrent lots

### 7. Input Validation

#### [src/components/config/FillerSettings.tsx:44](frontend/src/components/config/FillerSettings.tsx#L44)
- **Issue**: Basic alert for validation, no proper checks
- **Required**:
  - Validate negative numbers
  - Validate reasonable value ranges
  - Check capacity vs max concurrent lots relationship
  - Add field-level validation UI

#### [src/pages/ScheduleCreate.tsx:67](frontend/src/pages/ScheduleCreate.tsx#L67)
- **Issue**: Basic validation, needs improvement
- **Required**:
  - Add file size validation for CSV upload
  - Validate CSV content before upload
  - Check for required columns
  - Validate data types in CSV

#### [src/components/visualization/GanttChart.tsx:66](frontend/src/components/visualization/GanttChart.tsx#L66)
- **Issue**: No handling for empty activities with numFillers set
- **Required**:
  - Validate activity data (no negative times)
  - Handle empty activities array gracefully
  - Show meaningful error messages

### 8. Missing Features

#### [src/router.tsx:64](frontend/src/router.tsx#L64)
- **Issue**: Profile page shows "Coming Soon"
- **Required**:
  - Create Profile component
  - Implement user settings
  - Add password change functionality
  - Display user information

#### [src/router.tsx:72](frontend/src/router.tsx#L72)
- **Issue**: 404 page is simple div
- **Required**:
  - Create proper NotFound component
  - Add navigation back to home
  - Show helpful error message
  - Add search functionality

---

## 🟢 Medium Priority (Nice to Have)

### 9. Code Cleanup - Remove Debug Logging

Remove all `console.log` and debug statements (keep error logging where appropriate):

#### [src/hooks/useKeyboardShortcuts.ts:61](frontend/src/hooks/useKeyboardShortcuts.ts#L61)
```typescript
console.log('Help dialog would open here');
```

#### [src/contexts/RealTimeContext.tsx](frontend/src/contexts/RealTimeContext.tsx)
- **Line 40**: `console.log('WebSocket message received:', message);`
- **Line 75**: `console.log('WebSocket connected, resubscribing to schedules...');`

#### [src/pages/Config.tsx](frontend/src/pages/Config.tsx)
- **Line 33**: `console.log('Saving configuration...');`
- **Line 42**: `console.log('Resetting to defaults...');`

#### [src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx)
- **Line 62**: `console.error('Failed to fetch schedules:', error);` - Use toast instead
- **Line 98**: `console.error('Failed to delete schedule:', error);` - Use toast instead

#### [src/hooks/useWebSocket.ts](frontend/src/hooks/useWebSocket.ts)
- **Line 72**: `console.warn('WebSocket is not connected...');`
- **Line 81**: `console.log('WebSocket already connected');`
- **Line 93**: `console.log('WebSocket connected');`
- **Line 110**: `console.error('WebSocket error:', error);`
- **Line 116**: `console.log('WebSocket disconnected');`
- **Line 123-124**: Reconnection attempt logging
- **Line 131**: `console.error('Max reconnection attempts reached');`
- **Line 138**: `console.error('Failed to create WebSocket connection:', error);`

#### [src/components/dashboard/RecentSchedulesTable.tsx](frontend/src/components/dashboard/RecentSchedulesTable.tsx)
- **Line 109**: `console.log('View schedule:', id);`
- **Line 117**: `console.log('Delete schedule:', id);`

#### [src/pages/ScheduleDetail.tsx:104](frontend/src/pages/ScheduleDetail.tsx#L104)
```typescript
console.log(`Exporting schedule ${id} as ${format}`);
```

#### [src/pages/ScheduleCreate.tsx](frontend/src/pages/ScheduleCreate.tsx)
- **Line 90**: `console.error('Schedule creation failed:', err);`
- **Line 91**: `console.error('Error response:', err.response?.data);`

### 10. Mock Data Removal

#### [src/components/dashboard/RecentSchedulesTable.tsx:21-73](frontend/src/components/dashboard/RecentSchedulesTable.tsx#L21-L73)
- **Issue**: Mock schedules data as fallback
- **Required**: Ensure API integration is complete, remove mock data

#### [src/test/mocks.ts:49](frontend/src/test/mocks.ts#L49)
- **Issue**: Test email 'test@example.com'
- **Note**: This is okay for testing, ensure not used in production

### 11. API Consistency

#### [src/api/schedules.ts](frontend/src/api/schedules.ts)
- **Issue**: Inconsistent endpoint naming (singular vs plural)
  - Line 83: POST to `/schedule` (singular)
  - Line 117: GET from `/schedules` (plural)
  - Line 124: GET from `/schedule/{id}` (singular)
  - Line 131: DELETE to `/schedule/{id}` (singular)
- **Required**:
  - Standardize to either all singular or all plural
  - Update backend API if needed
  - Document API conventions

#### [src/api/schedules.ts:6](frontend/src/api/schedules.ts#L6)
- **Issue**: API_BASE_URL has fallback to localhost
- **Required**: Enforce environment variable requirement
- **Impact**: Production deployments could use wrong API

### 12. Hardcoded Configuration Values

#### [src/hooks/useWebSocket.ts](frontend/src/hooks/useWebSocket.ts)
- **Line 45**: WebSocket URL defaults to localhost
- **Line 47**: Reconnect interval hardcoded to 3000ms
- **Line 48**: Max reconnect attempts hardcoded to 5
- **Required**:
  - Move to environment variables or config
  - Make configurable via UI settings
  - Add exponential backoff for reconnection

#### [src/components/visualization/GanttChart.tsx](frontend/src/components/visualization/GanttChart.tsx)
- **Line 29-38**: Color palette hardcoded
- **Line 44**: Default numFillers = 4
- **Required**:
  - Use theme-based colors
  - Make defaults configurable

#### [src/pages/Compare.tsx](frontend/src/pages/Compare.tsx)
- **Line 23**: Hardcoded limit of 100 schedules
- **Line 45**: Maximum 4 schedules for comparison
- **Required**: Make configurable or use pagination

### 13. Type Safety Improvements

#### [src/components/visualization/GanttChart.tsx:79](frontend/src/components/visualization/GanttChart.tsx#L79)
- **Issue**: `any` type for CustomTooltip payload parameter
- **Required**: Use proper Recharts types
```typescript
import { TooltipProps } from 'recharts';
```

#### [src/pages/Login.tsx & Register.tsx](frontend/src/pages/Login.tsx)
- **Lines 65, 112**: `err: any` catch blocks
- **Required**: Use `unknown` and type guard, or proper error types

---

## 🔵 Low Priority (Future Enhancements)

### 14. Performance Optimizations

#### Large Dataset Handling
- **Location**: [src/components/dashboard/RecentSchedulesTable.tsx](frontend/src/components/dashboard/RecentSchedulesTable.tsx)
- **Issue**: No virtualization for long lists
- **Required**:
  - Implement virtual scrolling for large tables
  - Add pagination to API calls
  - Lazy load data

#### Chart Rendering
- **Location**: [src/components/visualization/GanttChart.tsx](frontend/src/components/visualization/GanttChart.tsx)
- **Issue**: No memoization for expensive calculations
- **Required**:
  - Use React.memo for chart components
  - Memoize calculated data
  - Optimize re-renders

#### WebSocket Optimization
- **Issue**: No exponential backoff for reconnection
- **Required**:
  - Implement exponential backoff
  - Add jitter to prevent thundering herd
  - Show connection quality indicator

### 15. Accessibility Improvements

#### Missing ARIA Labels
- **Location**: Various buttons and interactive elements
- **Required**:
  - Add aria-labels for screen readers
  - Ensure keyboard navigation works
  - Add focus indicators
  - Test with screen readers

#### Better Loading States
- **Location**: Various components
- **Required**:
  - Add skeleton loaders
  - Show progress indicators
  - Implement optimistic UI updates

### 16. Enhanced Empty States

#### [src/components/dashboard/RecentSchedulesTable.tsx](frontend/src/components/dashboard/RecentSchedulesTable.tsx)
- **Current**: Basic empty state message
- **Enhanced**:
  - Add illustration
  - Show actionable suggestions
  - Add "Create Schedule" button
  - Show helpful tips

### 17. Real-time Features Enhancement

#### Live Progress Updates
- **Location**: Schedule detail pages
- **Required**:
  - Show real-time progress bars
  - Update status automatically
  - Show live completion percentage
  - Add progress notifications

#### Polling Fallback
- **Issue**: No fallback if WebSocket fails
- **Required**:
  - Implement polling as fallback
  - Auto-switch between WebSocket and polling
  - Show connection method to user

#### Desktop Notifications
- **Location**: Settings mention notifications but not implemented
- **Required**:
  - Request notification permissions
  - Send desktop notifications for:
    - Schedule completion
    - Schedule failures
    - System alerts
  - Make configurable in settings

---

## 📊 Summary Statistics

### By Priority
- **Critical**: 7 major issues
- **High**: 9 areas needing fixes
- **Medium**: 7 improvements needed
- **Low**: 4 future enhancements

### By Category
- **Missing Features**: 8 items
- **Configuration**: 6 items
- **Error Handling**: 5 items
- **Code Cleanup**: 20+ console.log statements
- **Validation**: 4 items
- **Performance**: 3 items
- **Type Safety**: 3 items
- **Accessibility**: 2 items

### Overall Progress
- ✅ **Completed**: Dashboard real-time data integration, Basic auth flow
- 🚧 **In Progress**: Configuration management, Export features
- ⏳ **Not Started**: Profile page, Enhanced notifications, Advanced optimizations

---

## 🎯 Suggested Implementation Order

### Phase 1: Core Functionality (Week 1-2)
1. Implement schedule deletion
2. Implement export functionality (CSV, JSON, PNG)
3. Connect Dashboard KPIs to real API
4. Connect Dashboard charts to real API
5. Create Schedules list page

### Phase 2: Configuration & Persistence (Week 2-3)
1. Implement configuration save/load API
2. Add configuration validation
3. Persist user preferences
4. Save strategy defaults

### Phase 3: Error Handling & UX (Week 3-4)
1. Add toast notifications for all errors
2. Improve WebSocket error handling
3. Add proper loading states
4. Enhance validation messages

### Phase 4: Polish & Enhancement (Week 4-5)
1. Remove all debug logging
2. Create Profile page
3. Create proper 404 page
4. Implement Help dialog
5. Standardize API endpoints

### Phase 5: Optimization & Accessibility (Week 5+)
1. Add virtualization for large lists
2. Improve type safety
3. Add accessibility features
4. Implement desktop notifications
5. Add performance optimizations

---

## 📝 Notes

- This list was generated by comprehensive code review on 2025-10-14
- Priority levels are suggestions and can be adjusted based on business needs
- Some items may be dependent on backend API changes
- Regular updates to this document are recommended as features are completed

---

## 🔗 Related Documents

- [Bug Report](bug_report.md) - Current known bugs
- [Progress Report](PROGRESS_REPORT.md) - Development progress tracking
- Backend API documentation (if available)
- Component documentation (if available)
