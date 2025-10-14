import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { LoadingButton } from '@/components/common/LoadingButton';

describe('LoadingButton', () => {
  it('renders button with children', () => {
    render(<LoadingButton>Click Me</LoadingButton>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('shows loading spinner when loading prop is true', () => {
    render(<LoadingButton loading>Submit</LoadingButton>);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('is disabled when loading', () => {
    render(<LoadingButton loading>Submit</LoadingButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is not disabled when loading prop is false', () => {
    render(<LoadingButton loading={false}>Submit</LoadingButton>);
    expect(screen.getByRole('button')).not.toBeDisabled();
  });

  it('handles click events when not loading', () => {
    let clicked = false;
    render(<LoadingButton onClick={() => { clicked = true; }}>Click</LoadingButton>);

    screen.getByRole('button').click();
    expect(clicked).toBe(true);
  });

  it('applies custom props', () => {
    render(
      <LoadingButton color="secondary" variant="outlined" data-testid="custom-button">
        Custom
      </LoadingButton>
    );

    const button = screen.getByTestId('custom-button');
    expect(button).toBeInTheDocument();
  });
});
