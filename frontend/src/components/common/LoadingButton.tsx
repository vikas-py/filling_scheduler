import { Button, CircularProgress, type ButtonProps } from '@mui/material';

interface LoadingButtonProps extends ButtonProps {
  loading?: boolean;
}

export const LoadingButton = ({ loading, disabled, children, ...props }: LoadingButtonProps) => {
  return (
    <Button
      {...props}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={20} /> : props.startIcon}
    >
      {children}
    </Button>
  );
};
