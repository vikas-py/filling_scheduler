import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { Dashboard } from '@/pages/Dashboard';

describe('Dashboard Integration', () => {
  it('renders dashboard page', () => {
    render(<Dashboard />);

    // Check for main heading
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
  });

  it('shows KPI cards section', () => {
    render(<Dashboard />);

    // Should show KPI section with specific heading
    const heading = screen.getByRole('heading', { name: /Total Schedules/i });
    expect(heading).toBeInTheDocument();
  });

  it('displays page structure', () => {
    const { container } = render(<Dashboard />);

    // Check that component renders without crashing
    expect(container).toBeTruthy();
    expect(container.firstChild).toBeTruthy();
  });
});
