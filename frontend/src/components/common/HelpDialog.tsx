import { Dialog, DialogTitle, DialogContent, Box, Typography, Chip, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import KeyboardIcon from '@mui/icons-material/Keyboard';
import { KEYBOARD_SHORTCUTS } from '@/hooks/useKeyboardShortcuts';

interface HelpDialogProps {
  open: boolean;
  onClose: () => void;
}

export const HelpDialog = ({ open, onClose }: HelpDialogProps) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      aria-labelledby="help-dialog-title"
    >
      <DialogTitle id="help-dialog-title" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <KeyboardIcon />
        Keyboard Shortcuts
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ marginLeft: 'auto' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {KEYBOARD_SHORTCUTS.map((shortcut, index) => {
            const keys = isMac ? shortcut.mac : shortcut.keys;
            return (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 1,
                }}
              >
                <Typography variant="body2">{shortcut.description}</Typography>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {keys.map((key, keyIndex) => (
                    <Chip
                      key={keyIndex}
                      label={key}
                      size="small"
                      sx={{
                        fontFamily: 'monospace',
                        fontWeight: 'bold',
                        minWidth: 36,
                      }}
                    />
                  ))}
                </Box>
              </Box>
            );
          })}
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 3, display: 'block' }}>
          Tip: Press these shortcuts from anywhere in the app (except when typing in a field).
        </Typography>
      </DialogContent>
    </Dialog>
  );
};
