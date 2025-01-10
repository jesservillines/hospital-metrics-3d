import React, { useEffect, useState } from 'react';
import axios from 'axios';
import * as SliderPrimitive from "@radix-ui/react-slider";
import { format } from 'date-fns';
import { Card } from '@/components/ui/card';

interface DateSliderProps {
  onDateChange: (date: string) => void;
}

export function DateSlider({ onDateChange }: DateSliderProps) {
  const [minDate, setMinDate] = useState<Date | null>(null);
  const [maxDate, setMaxDate] = useState<Date | null>(null);
  const [currentValue, setCurrentValue] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDateRange = async () => {
      try {
        console.log('Fetching date range...');
        const response = await axios.get('http://localhost:8000/api/v1/metrics/date-range', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          }
        });
        
        const { min_date, max_date } = response.data;
        console.log('Date range received:', { min_date, max_date });
        
        const minDateObj = new Date(min_date);
        const maxDateObj = new Date(max_date);
        
        setMinDate(minDateObj);
        setMaxDate(maxDateObj);
        setCurrentValue(maxDateObj.getTime());
        onDateChange(max_date);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching date range:', error);
        setError('Failed to load date range');
        setIsLoading(false);
      }
    };

    fetchDateRange();
  }, [onDateChange]);

  const handleSliderChange = (value: number[]) => {
    try {
      const dateValue = value[0];
      setCurrentValue(dateValue);
      const formattedDate = format(new Date(dateValue), 'yyyy-MM-dd');
      console.log('Date slider changed:', { dateValue, formattedDate });
      onDateChange(formattedDate);
    } catch (error) {
      console.error('Error handling slider change:', error);
      setError('Failed to update date');
    }
  };

  if (isLoading || !minDate || !maxDate) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm p-4 shadow-lg z-50">
        <div className="max-w-4xl mx-auto text-center text-sm text-gray-600">
          Loading date range...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-red-50/90 backdrop-blur-sm p-4 shadow-lg z-50">
        <div className="max-w-4xl mx-auto text-center text-sm text-red-600">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-auto">
      <Card className="mx-4 mb-4 bg-white/95 backdrop-blur-sm shadow-lg rounded-lg">
        <div className="p-4">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-600 min-w-[100px]">
              {format(minDate, 'MMM d, yyyy')}
            </span>
            <div className="flex-1 px-2">
              <SliderPrimitive.Root
                value={[currentValue]}
                min={minDate.getTime()}
                max={maxDate.getTime()}
                step={86400000}
                onValueChange={handleSliderChange}
                className="relative flex w-full touch-none select-none items-center"
              >
                <SliderPrimitive.Track className="relative h-2 w-full grow overflow-hidden rounded-full bg-slate-200">
                  <SliderPrimitive.Range className="absolute h-full bg-blue-500" />
                </SliderPrimitive.Track>
                <SliderPrimitive.Thumb
                  className="block h-5 w-5 rounded-full border-2 border-blue-500 bg-white ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                />
              </SliderPrimitive.Root>
            </div>
            <span className="text-sm font-medium text-gray-600 min-w-[100px] text-right">
              {format(maxDate, 'MMM d, yyyy')}
            </span>
          </div>
          <div className="text-center mt-2">
            <span className="text-sm font-semibold text-gray-900">
              Selected: {format(new Date(currentValue), 'MMMM d, yyyy')}
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default DateSlider;
