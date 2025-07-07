import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import { Box, Paper, Typography } from '@mui/material';

// Chart.js 등록
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface RadarChartProps {
  data: {
    [key: string]: number;
  };
  compareData?: {
    [key: string]: number;
  };
  title?: string;
  height?: number;
}

const AIRISS_DIMENSIONS = [
  { name: '업무성과', color: '#FF5722' },
  { name: 'KPI달성', color: '#4A4A4A' },
  { name: '태도마인드', color: '#F89C26' },
  { name: '커뮤니케이션', color: '#B3B3B3' },
  { name: '리더십협업', color: '#FF8A50' },
  { name: '전문성학습', color: '#6A6A6A' },
  { name: '창의혁신', color: '#FFA726' },
  { name: '조직적응', color: '#9E9E9E' },
];

const RadarChart: React.FC<RadarChartProps> = ({ 
  data, 
  compareData, 
  title = 'AIRISS 8대 영역 분석',
  height = 400 
}) => {
  const labels = AIRISS_DIMENSIONS.map(dim => dim.name);
  const values = labels.map(label => data[label] || 0);
  const compareValues = compareData ? labels.map(label => compareData[label] || 0) : null;

  const chartData = {
    labels,
    datasets: [
      {
        label: '개인 점수',
        data: values,
        backgroundColor: 'rgba(255, 87, 34, 0.2)',
        borderColor: '#FF5722',
        borderWidth: 3,
        pointBackgroundColor: '#FF5722',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
      ...(compareValues ? [{
        label: '평균 점수',
        data: compareValues,
        backgroundColor: 'rgba(74, 74, 74, 0.1)',
        borderColor: '#4A4A4A',
        borderWidth: 2,
        pointBackgroundColor: '#4A4A4A',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderDash: [5, 5],
      }] : []),
    ],
  };

  const options: ChartOptions<'radar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: ${context.raw}점`;
          },
        },
      },
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        beginAtZero: true,
        ticks: {
          stepSize: 20,
          font: {
            size: 12,
          },
        },
        pointLabels: {
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 3, height: height + 80 }}>
      <Typography variant="h6" gutterBottom align="center">
        {title}
      </Typography>
      <Box sx={{ height, position: 'relative' }}>
        <Radar data={chartData} options={options} />
      </Box>
    </Paper>
  );
};

export default RadarChart;