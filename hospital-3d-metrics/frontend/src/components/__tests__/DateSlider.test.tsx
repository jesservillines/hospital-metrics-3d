import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DateSlider } from '../DateSlider';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('DateSlider', () => {
  const mockOnDateChange = jest.fn();
  const mockDateRange = {
    min_date: '2024-01-01',
    max_date: '2024-12-31'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock successful API response
    mockedAxios.get.mockResolvedValue({ data: mockDateRange });
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'mock-token'),
      },
      writable: true
    });
  });

  it('renders loading state initially', () => {
    render(<DateSlider onDateChange={mockOnDateChange} />);
    expect(screen.getByText('Loading date range...')).toBeInTheDocument();
  });

  it('fetches date range on mount', async () => {
    render(<DateSlider onDateChange={mockOnDateChange} />);
    
    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/metrics/date-range',
      expect.any(Object)
    );

    await waitFor(() => {
      expect(screen.getByText(/December 31, 2024/)).toBeInTheDocument();
    });
  });

  it('calls onDateChange with max date initially', async () => {
    render(<DateSlider onDateChange={mockOnDateChange} />);

    await waitFor(() => {
      expect(mockOnDateChange).toHaveBeenCalledWith(mockDateRange.max_date);
    });
  });

  it('handles API error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('API Error'));
    
    render(<DateSlider onDateChange={mockOnDateChange} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load date range')).toBeInTheDocument();
    });
  });

  it('displays formatted date range', async () => {
    render(<DateSlider onDateChange={mockOnDateChange} />);

    await waitFor(() => {
      expect(screen.getByText(/Jan 1, 2024/)).toBeInTheDocument();
      expect(screen.getByText(/Dec 31, 2024/)).toBeInTheDocument();
    });
  });
});
