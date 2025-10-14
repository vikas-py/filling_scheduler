import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Hook for global keyboard shortcuts
 *
 * Keyboard shortcuts:
 * - Ctrl+/ (or Cmd+/): Show help dialog
 * - Ctrl+N (or Cmd+N): New schedule
 * - Ctrl+D (or Cmd+D): Dashboard
 * - Ctrl+C (or Cmd+C): Compare schedules
 * - Ctrl+, (or Cmd+,): Settings/Config
 * - Escape: Close modals/dialogs
 */
export const useKeyboardShortcuts = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifier = isMac ? event.metaKey : event.ctrlKey;

      // Ignore shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      // New schedule: Ctrl+N / Cmd+N
      if (modifier && event.key === 'n') {
        event.preventDefault();
        navigate('/schedules/create');
      }

      // Dashboard: Ctrl+D / Cmd+D
      if (modifier && event.key === 'd') {
        event.preventDefault();
        navigate('/dashboard');
      }

      // Compare: Ctrl+K / Cmd+K
      if (modifier && event.key === 'k') {
        event.preventDefault();
        navigate('/compare');
      }

      // Settings: Ctrl+, / Cmd+,
      if (modifier && event.key === ',') {
        event.preventDefault();
        navigate('/config');
      }

      // Help dialog: Ctrl+/ / Cmd+/
      if (modifier && event.key === '/') {
        event.preventDefault();
        // Show help dialog (implementation depends on dialog component)
        console.log('Help dialog would open here');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);
};

/**
 * Keyboard shortcuts reference
 */
export const KEYBOARD_SHORTCUTS = [
  { keys: ['Ctrl', 'N'], mac: ['⌘', 'N'], description: 'Create new schedule' },
  { keys: ['Ctrl', 'D'], mac: ['⌘', 'D'], description: 'Go to dashboard' },
  { keys: ['Ctrl', 'K'], mac: ['⌘', 'K'], description: 'Compare schedules' },
  { keys: ['Ctrl', ','], mac: ['⌘', ','], description: 'Open settings' },
  { keys: ['Ctrl', '/'], mac: ['⌘', '/'], description: 'Show help' },
  { keys: ['Esc'], mac: ['Esc'], description: 'Close dialogs' },
];
