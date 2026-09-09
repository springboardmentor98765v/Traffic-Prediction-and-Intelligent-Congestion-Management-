export interface RoadNode {
  id: string;
  name: string;
  status: 'Flowing' | 'Moderate' | 'Congested';
  coords: string;
  count: string;
  density: string;
}

export const initialRoadNodes: RoadNode[] = [
  { id: 'jm-road', name: 'JM Road Node', status: 'Congested', coords: '18.5204, 73.8567', count: '450 vehicles/min', density: '85%' },
  { id: 'fc-road', name: 'FC Road Node', status: 'Flowing', coords: '18.5284, 73.8417', count: '120 vehicles/min', density: '25%' },
  { id: 'karve-road', name: 'Karve Road Node', status: 'Moderate', coords: '18.5074, 73.8277', count: '280 vehicles/min', density: '55%' },
  { id: 'baner-road', name: 'Baner Main Node', status: 'Flowing', coords: '18.559, 73.7868', count: '90 vehicles/min', density: '18%' },
];

export const validatePasswordRules = (pass: string): string => {
  if (pass.length < 8) return 'Password must be at least 8 characters long.';
  if (!/[A-Z]/.test(pass)) return 'Password must contain at least 1 uppercase character.';
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(pass)) return 'Password must contain at least 1 special character.';
  return '';
};
