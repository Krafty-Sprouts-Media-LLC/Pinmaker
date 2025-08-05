import React, { useState, useCallback } from 'react';
import { HexColorPicker, HexColorInput } from 'react-colorful';
import { Palette, RotateCcw } from 'lucide-react';
import { ColorPickerProps } from '../types';

const ColorPicker: React.FC<ColorPickerProps> = ({
  color,
  onChange,
  presetColors = [],
  showPresets = true,
  showInput = true,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [tempColor, setTempColor] = useState(color);

  const defaultPresets = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2',
    '#000000', '#FFFFFF', '#808080', '#FF0000', '#00FF00',
    '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500'
  ];

  const presets = presetColors.length > 0 ? presetColors : defaultPresets;

  const handleColorChange = useCallback((newColor: string) => {
    setTempColor(newColor);
    onChange(newColor);
  }, [onChange]);

  const handlePresetClick = useCallback((presetColor: string) => {
    handleColorChange(presetColor);
    setIsOpen(false);
  }, [handleColorChange]);

  const resetToOriginal = useCallback(() => {
    handleColorChange(color);
    setTempColor(color);
  }, [color, handleColorChange]);

  const renderColorButton = () => (
    <button
      onClick={() => !disabled && setIsOpen(!isOpen)}
      disabled={disabled}
      className={`relative w-10 h-10 rounded-lg border-2 border-gray-300 overflow-hidden transition-all ${
        disabled
          ? 'cursor-not-allowed opacity-50'
          : 'hover:border-gray-400 cursor-pointer'
      } ${
        isOpen ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      }`}
      title="Click to change color"
    >
      <div
        className="w-full h-full"
        style={{ backgroundColor: tempColor }}
      />
      <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 bg-black bg-opacity-20 transition-opacity">
        <Palette size={16} className="text-white" />
      </div>
    </button>
  );

  const renderPresets = () => {
    if (!showPresets) return null;

    return (
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Preset Colors</h4>
        <div className="grid grid-cols-10 gap-2">
          {presets.map((presetColor, index) => (
            <button
              key={index}
              onClick={() => handlePresetClick(presetColor)}
              className={`w-6 h-6 rounded border-2 transition-all hover:scale-110 ${
                tempColor.toLowerCase() === presetColor.toLowerCase()
                  ? 'border-gray-800 ring-2 ring-blue-500'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              style={{ backgroundColor: presetColor }}
              title={presetColor}
            />
          ))}
        </div>
      </div>
    );
  };

  const renderColorInput = () => {
    if (!showInput) return null;

    return (
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Hex Color
        </label>
        <div className="flex items-center space-x-2">
          <div className="flex-1">
            <HexColorInput
              color={tempColor}
              onChange={handleColorChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="#000000"
            />
          </div>
          <button
            onClick={resetToOriginal}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="Reset to original color"
          >
            <RotateCcw size={16} />
          </button>
        </div>
      </div>
    );
  };

  const renderColorPicker = () => {
    if (!isOpen) return null;

    return (
      <div className="absolute top-12 left-0 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[280px]">
        {renderPresets()}
        
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Custom Color</h4>
          <HexColorPicker
            color={tempColor}
            onChange={handleColorChange}
            className="w-full"
          />
        </div>
        
        {renderColorInput()}
        
        <div className="mt-4 flex items-center justify-between pt-3 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <div
              className="w-8 h-8 rounded border border-gray-300"
              style={{ backgroundColor: color }}
              title="Original color"
            />
            <span className="text-xs text-gray-500">→</span>
            <div
              className="w-8 h-8 rounded border border-gray-300"
              style={{ backgroundColor: tempColor }}
              title="New color"
            />
          </div>
          
          <button
            onClick={() => setIsOpen(false)}
            className="px-3 py-1 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="relative inline-block">
      {renderColorButton()}
      {renderColorPicker()}
      
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default ColorPicker;