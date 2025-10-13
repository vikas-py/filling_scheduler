import { Container, Typography, Paper } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'

export const Dashboard = () => {
  const { user } = useAuth()

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Welcome, {user?.email}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          This is your dashboard. Schedule management features coming soon!
        </Typography>
      </Paper>
    </Container>
  )
}
