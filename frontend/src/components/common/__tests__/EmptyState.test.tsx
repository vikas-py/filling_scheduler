import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { EmptyState } from '@/components/common/EmptyState';
import { Inbox as InboxIcon } from '@mui/icons-material';

describe('EmptyState', () => {
  it('renders with title', () => {
    render(<EmptyState title="No data" />);
    expect(screen.getByText('No data')).toBeInTheDocument();
  });

  it('renders with description', () => {
    render(<EmptyState title="No data" description="Try adding some items" />);
    expect(screen.getByText('Try adding some items')).toBeInTheDocument();
  });

  it('renders with custom icon', () => {
    render(<EmptyState title="No data" icon={<InboxIcon data-testid="custom-icon" />} />);
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('renders with action button', () => {
    const handleClick = () => {};
    render(
      <EmptyState
        title="No data"
        action={{
          label: 'Add Item',
          onClick: handleClick,
        }}
      />
    );
    expect(screen.getByRole('button', { name: 'Add Item' })).toBeInTheDocument();
  });

  it('calls action onClick when button is clicked', () => {
    let clicked = false;
    const handleClick = () => {
      clicked = true;
    };

    render(
      <EmptyState
        title="No data"
        action={{
          label: 'Add Item',
          onClick: handleClick,
        }}
      />
    );

    const button = screen.getByRole('button', { name: 'Add Item' });
    button.click();
    expect(clicked).toBe(true);
  });
});
