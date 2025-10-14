import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { ConnectionStatus } from '@/components/common/ConnectionStatus';
import type { WebSocketStatus } from '@/hooks/useWebSocket';

describe('ConnectionStatus', () => {
  it('shows Connected status when connected', () => {
    render(<ConnectionStatus status="connected" />);
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('shows Connecting status when connecting', () => {
    render(<ConnectionStatus status="connecting" />);
    expect(screen.getByText('Connecting')).toBeInTheDocument();
  });

  it('shows Offline status when disconnected', () => {
    render(<ConnectionStatus status="disconnected" />);
    expect(screen.getByText('Offline')).toBeInTheDocument();
  });

  it('shows Error status on error', () => {
    render(<ConnectionStatus status="error" />);
    expect(screen.getByText('Error')).toBeInTheDocument();
  });

  it('calls onReconnect when error status chip is clicked', () => {
    const handleReconnect = vi.fn();
    render(<ConnectionStatus status="error" onReconnect={handleReconnect} />);

    const chip = screen.getByText('Error');
    chip.click();

    expect(handleReconnect).toHaveBeenCalledTimes(1);
  });

  it('does not call onReconnect for non-error statuses', () => {
    const handleReconnect = vi.fn();
    const statuses: WebSocketStatus[] = ['connected', 'connecting', 'disconnected'];

    statuses.forEach((status) => {
      const { unmount } = render(<ConnectionStatus status={status} onReconnect={handleReconnect} />);
      const chip = screen.getByRole('button');
      chip.click();
      unmount();
    });

    expect(handleReconnect).not.toHaveBeenCalled();
  });
});
