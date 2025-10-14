import { Skeleton, Box, Card, CardContent, Stack } from '@mui/material';

export const TableSkeleton = ({ rows = 5, columns = 5 }: { rows?: number; columns?: number }) => (
  <Box>
    {Array.from({ length: rows }).map((_, i) => (
      <Box key={i} sx={{ display: 'flex', gap: 2, mb: 2 }}>
        {Array.from({ length: columns }).map((_, j) => (
          <Skeleton key={j} variant="text" width={`${100 / columns}%`} height={40} />
        ))}
      </Box>
    ))}
  </Box>
);

export const CardSkeleton = ({ count = 4 }: { count?: number }) => (
  <Stack direction="row" spacing={2} sx={{ flexWrap: 'wrap' }}>
    {Array.from({ length: count }).map((_, i) => (
      <Card key={i} sx={{ flex: '1 1 200px' }}>
        <CardContent>
          <Skeleton variant="text" width="60%" height={24} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="40%" height={40} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="80%" height={20} />
        </CardContent>
      </Card>
    ))}
  </Stack>
);

export const ChartSkeleton = ({ height = 400 }: { height?: number }) => (
  <Box sx={{ width: '100%', height }}>
    <Skeleton variant="rectangular" width="100%" height="100%" />
  </Box>
);

export const ListSkeleton = ({ items = 5 }: { items?: number }) => (
  <Stack spacing={2}>
    {Array.from({ length: items }).map((_, i) => (
      <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Skeleton variant="circular" width={40} height={40} />
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width="40%" height={24} />
          <Skeleton variant="text" width="80%" height={20} />
        </Box>
      </Box>
    ))}
  </Stack>
);

export const FormSkeleton = ({ fields = 5 }: { fields?: number }) => (
  <Stack spacing={3}>
    {Array.from({ length: fields }).map((_, i) => (
      <Box key={i}>
        <Skeleton variant="text" width="30%" height={24} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" width="100%" height={56} />
      </Box>
    ))}
  </Stack>
);

export const PageSkeleton = () => (
  <Box>
    <Skeleton variant="text" width="40%" height={48} sx={{ mb: 3 }} />
    <CardSkeleton count={4} />
    <Box sx={{ mt: 4 }}>
      <ChartSkeleton />
    </Box>
  </Box>
);
