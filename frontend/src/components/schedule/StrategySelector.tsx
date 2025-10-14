import {
  Box,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Radio,
  Stack,
  Chip,
} from '@mui/material';
import { Timer, Speed, Bolt, Psychology, AutoGraph } from '@mui/icons-material';

export type StrategyType = 'LPT' | 'SPT' | 'CFS' | 'Hybrid' | 'MILP';

interface Strategy {
  id: StrategyType;
  name: string;
  description: string;
  icon: React.ReactNode;
  complexity: 'Low' | 'Medium' | 'High';
  recommended?: boolean;
}

interface StrategySelectorProps {
  selectedStrategy: StrategyType | null;
  onStrategySelect: (strategy: StrategyType) => void;
}

const strategies: Strategy[] = [
  {
    id: 'LPT',
    name: 'Longest Processing Time',
    description: 'Schedules lots with the longest fill time first. Good for balancing workload across fillers.',
    icon: <Timer sx={{ fontSize: 40 }} />,
    complexity: 'Low',
  },
  {
    id: 'SPT',
    name: 'Shortest Processing Time',
    description: 'Schedules lots with the shortest fill time first. Minimizes average completion time.',
    icon: <Speed sx={{ fontSize: 40 }} />,
    complexity: 'Low',
  },
  {
    id: 'CFS',
    name: 'Critical Fill Strategy',
    description: 'Prioritizes critical lots based on custom rules and constraints.',
    icon: <Bolt sx={{ fontSize: 40 }} />,
    complexity: 'Medium',
  },
  {
    id: 'Hybrid',
    name: 'Hybrid Packing',
    description: 'Combines multiple strategies for balanced optimization. Recommended for most use cases.',
    icon: <Psychology sx={{ fontSize: 40 }} />,
    complexity: 'Medium',
    recommended: true,
  },
  {
    id: 'MILP',
    name: 'Mixed Integer Linear Programming',
    description: 'Uses mathematical optimization for optimal schedules. Best for complex scenarios with many constraints.',
    icon: <AutoGraph sx={{ fontSize: 40 }} />,
    complexity: 'High',
  },
];

const getComplexityColor = (complexity: string) => {
  switch (complexity) {
    case 'Low':
      return 'success';
    case 'Medium':
      return 'warning';
    case 'High':
      return 'error';
    default:
      return 'default';
  }
};

export const StrategySelector = ({ selectedStrategy, onStrategySelect }: StrategySelectorProps) => {
  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Select a scheduling strategy that best fits your requirements. Each strategy has different trade-offs between speed and optimality.
      </Typography>

      <Stack spacing={2}>
        {strategies.map((strategy) => (
          <Card
            key={strategy.id}
            variant="outlined"
            sx={{
              borderWidth: selectedStrategy === strategy.id ? 2 : 1,
              borderColor: selectedStrategy === strategy.id ? 'primary.main' : 'divider',
              position: 'relative',
            }}
          >
            <CardActionArea onClick={() => onStrategySelect(strategy.id)}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  <Radio
                    checked={selectedStrategy === strategy.id}
                    value={strategy.id}
                    sx={{ mt: 0.5 }}
                  />

                  <Box sx={{ color: 'primary.main' }}>{strategy.icon}</Box>

                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="h6" component="div">
                        {strategy.name}
                      </Typography>
                      {strategy.recommended && (
                        <Chip label="Recommended" color="success" size="small" />
                      )}
                      <Chip
                        label={strategy.complexity}
                        color={getComplexityColor(strategy.complexity)}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {strategy.description}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Stack>
    </Box>
  );
};
