import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Settings, LogOut, User, Palette } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { ChromePicker } from 'react-color';

interface SettingsWidgetProps {
  onColorChange: (color: string) => void;
  currentColor: string;
}

export function SettingsWidget({ onColorChange, currentColor }: SettingsWidgetProps) {
  const { logout } = useAuth();
  const [showColorPicker, setShowColorPicker] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="w-10 h-10 rounded-full bg-white shadow-lg hover:bg-gray-100"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-48" align="end">
          <div className="space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => {}}
            >
              <User className="mr-2 h-4 w-4" />
              Profile
            </Button>
            
            <Popover open={showColorPicker} onOpenChange={setShowColorPicker}>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  className="w-full justify-start"
                >
                  <Palette className="mr-2 h-4 w-4" />
                  Heatmap Color
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <ChromePicker
                  color={currentColor}
                  onChange={(color) => onColorChange(color.hex)}
                />
              </PopoverContent>
            </Popover>

            <Button
              variant="ghost"
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={handleLogout}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
