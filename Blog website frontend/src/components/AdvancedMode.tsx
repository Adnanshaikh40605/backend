
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Settings, Palette, Type, Layout, Eye } from 'lucide-react';

interface AdvancedModeProps {
  isOpen: boolean;
  onClose: () => void;
}

const AdvancedMode: React.FC<AdvancedModeProps> = ({ isOpen, onClose }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [fontSize, setFontSize] = useState([16]);
  const [layout, setLayout] = useState('default');
  const [theme, setTheme] = useState('red');
  const [animations, setAnimations] = useState(true);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-red-500" />
            <CardTitle>Advanced Mode Settings</CardTitle>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            ✕
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Display Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Eye className="w-4 h-4 text-red-500" />
              <h3 className="font-semibold">Display Settings</h3>
            </div>
            <div className="space-y-4 pl-6">
              <div className="flex items-center justify-between">
                <Label htmlFor="dark-mode">Dark Mode</Label>
                <Switch
                  id="dark-mode"
                  checked={darkMode}
                  onCheckedChange={setDarkMode}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Font Size: {fontSize[0]}px</Label>
                <Slider
                  value={fontSize}
                  onValueChange={setFontSize}
                  max={24}
                  min={12}
                  step={1}
                  className="w-full"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="animations">Enable Animations</Label>
                <Switch
                  id="animations"
                  checked={animations}
                  onCheckedChange={setAnimations}
                />
              </div>
            </div>
          </div>

          {/* Theme Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Palette className="w-4 h-4 text-red-500" />
              <h3 className="font-semibold">Theme Settings</h3>
            </div>
            <div className="space-y-4 pl-6">
              <div className="space-y-2">
                <Label>Color Theme</Label>
                <Select value={theme} onValueChange={setTheme}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="red">Red (Default)</SelectItem>
                    <SelectItem value="blue">Blue</SelectItem>
                    <SelectItem value="green">Green</SelectItem>
                    <SelectItem value="purple">Purple</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Layout Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Layout className="w-4 h-4 text-red-500" />
              <h3 className="font-semibold">Layout Settings</h3>
            </div>
            <div className="space-y-4 pl-6">
              <div className="space-y-2">
                <Label>Blog Layout</Label>
                <Select value={layout} onValueChange={setLayout}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Grid (Default)</SelectItem>
                    <SelectItem value="list">List View</SelectItem>
                    <SelectItem value="masonry">Masonry</SelectItem>
                    <SelectItem value="compact">Compact</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Typography Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Type className="w-4 h-4 text-red-500" />
              <h3 className="font-semibold">Typography Settings</h3>
            </div>
            <div className="space-y-4 pl-6">
              <div className="space-y-2">
                <Label>Reading Font</Label>
                <Select defaultValue="lexend">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lexend">Lexend (Default)</SelectItem>
                    <SelectItem value="inter">Inter</SelectItem>
                    <SelectItem value="roboto">Roboto</SelectItem>
                    <SelectItem value="opensans">Open Sans</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <Button 
              className="flex-1 bg-red-500 hover:bg-red-600"
              onClick={() => {
                // Apply settings logic would go here
                console.log('Applying settings:', { darkMode, fontSize, layout, theme, animations });
                onClose();
              }}
            >
              Apply Changes
            </Button>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdvancedMode;
