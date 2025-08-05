import React, { useState, useCallback } from 'react';
import { Type, Image, Move, Trash2, Copy, Eye, EyeOff, Lock, Unlock } from 'lucide-react';
import { ElementEditorProps, TextElement, ImageRegion, FontInfo } from '../types';
import ColorPicker from './ColorPicker';
import FontSelector from './FontSelector';

const ElementEditor: React.FC<ElementEditorProps> = ({
  element,
  fonts,
  onUpdate,
  onDelete,
  onDuplicate
}) => {
  const [localChanges, setLocalChanges] = useState<any>({});
  const [isLocked, setIsLocked] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  const isTextElement = 'text' in element;
  const isImageElement = 'placeholder_text' in element;

  const handleChange = useCallback((field: string, value: any) => {
    const newChanges = { ...localChanges, [field]: value };
    setLocalChanges(newChanges);
    onUpdate(newChanges);
  }, [localChanges, onUpdate]);

  const handlePositionChange = useCallback((field: 'x' | 'y' | 'width' | 'height', value: number) => {
    handleChange(field, Math.max(0, value));
  }, [handleChange]);

  const handleFontChange = useCallback((font: FontInfo) => {
    const updates = {
      font_family: font.family,
      ...(font.variants && font.variants.length > 0 && { font_weight: font.variants[0] })
    };
    
    Object.entries(updates).forEach(([key, value]) => {
      handleChange(key, value);
    });
  }, [handleChange]);

  const renderElementHeader = () => {
    const elementType = isTextElement ? 'Text' : 'Image';
    const icon = isTextElement ? Type : Image;
    const IconComponent = icon;

    return (
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <IconComponent size={16} className="text-gray-600" />
          <h4 className="font-medium text-gray-900">
            {elementType} Element
          </h4>
          <span className="text-xs text-gray-500 font-mono">
            #{element.id}
          </span>
        </div>
        
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setIsVisible(!isVisible)}
            className={`p-1 rounded transition-colors ${
              isVisible
                ? 'text-gray-600 hover:text-gray-800'
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title={isVisible ? 'Hide element' : 'Show element'}
          >
            {isVisible ? <Eye size={14} /> : <EyeOff size={14} />}
          </button>
          
          <button
            onClick={() => setIsLocked(!isLocked)}
            className={`p-1 rounded transition-colors ${
              isLocked
                ? 'text-red-600 hover:text-red-800'
                : 'text-gray-600 hover:text-gray-800'
            }`}
            title={isLocked ? 'Unlock element' : 'Lock element'}
          >
            {isLocked ? <Lock size={14} /> : <Unlock size={14} />}
          </button>
          
          {onDuplicate && (
            <button
              onClick={() => onDuplicate(element)}
              className="p-1 text-gray-600 hover:text-gray-800 rounded transition-colors"
              title="Duplicate element"
            >
              <Copy size={14} />
            </button>
          )}
          
          <button
            onClick={() => onDelete(element.id)}
            className="p-1 text-red-600 hover:text-red-800 rounded transition-colors"
            title="Delete element"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    );
  };

  const renderPositionControls = () => (
    <div className="space-y-4">
      <h5 className="text-sm font-medium text-gray-700 flex items-center space-x-2">
        <Move size={14} />
        <span>Position & Size</span>
      </h5>
      
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">X Position</label>
          <input
            type="number"
            value={localChanges.x ?? element.x}
            onChange={(e) => handlePositionChange('x', parseInt(e.target.value) || 0)}
            disabled={isLocked}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            min="0"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Y Position</label>
          <input
            type="number"
            value={localChanges.y ?? element.y}
            onChange={(e) => handlePositionChange('y', parseInt(e.target.value) || 0)}
            disabled={isLocked}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            min="0"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Width</label>
          <input
            type="number"
            value={localChanges.width ?? element.width}
            onChange={(e) => handlePositionChange('width', parseInt(e.target.value) || 0)}
            disabled={isLocked}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            min="1"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Height</label>
          <input
            type="number"
            value={localChanges.height ?? element.height}
            onChange={(e) => handlePositionChange('height', parseInt(e.target.value) || 0)}
            disabled={isLocked}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            min="1"
          />
        </div>
      </div>
    </div>
  );

  const renderTextControls = () => {
    if (!isTextElement) return null;
    
    const textElement = element as TextElement;
    
    return (
      <div className="space-y-4">
        {/* Text Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Text Content</label>
          <textarea
            value={localChanges.text ?? textElement.text}
            onChange={(e) => handleChange('text', e.target.value)}
            disabled={isLocked}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={3}
            placeholder="Enter text content..."
          />
        </div>
        
        {/* Font Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Font Family</label>
          <FontSelector
            fonts={fonts}
            selectedFont={fonts.find(f => f.family === (localChanges.font_family ?? textElement.font_family))}
            onFontChange={handleFontChange}
            disabled={isLocked}
            previewText={localChanges.text ?? textElement.text}
          />
        </div>
        
        {/* Font Properties */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Font Size</label>
            <input
              type="number"
              value={localChanges.font_size ?? textElement.font_size}
              onChange={(e) => handleChange('font_size', parseInt(e.target.value) || 12)}
              disabled={isLocked}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              min="8"
              max="200"
            />
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Font Weight</label>
            <select
              value={localChanges.font_weight ?? textElement.font_weight}
              onChange={(e) => handleChange('font_weight', e.target.value)}
              disabled={isLocked}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="normal">Normal</option>
              <option value="bold">Bold</option>
              <option value="100">Thin</option>
              <option value="300">Light</option>
              <option value="500">Medium</option>
              <option value="600">Semi Bold</option>
              <option value="700">Bold</option>
              <option value="800">Extra Bold</option>
              <option value="900">Black</option>
            </select>
          </div>
        </div>
        
        {/* Text Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Text Color</label>
          <div className="flex items-center space-x-3">
            <ColorPicker
              color={localChanges.color ?? textElement.color}
              onChange={(color) => handleChange('color', color)}
              disabled={isLocked}
            />
            <span className="text-sm text-gray-600 font-mono">
              {localChanges.color ?? textElement.color}
            </span>
          </div>
        </div>
        
        {/* Text Alignment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Text Alignment</label>
          <div className="flex space-x-2">
            {['left', 'center', 'right', 'justify'].map((align) => (
              <button
                key={align}
                onClick={() => handleChange('text_align', align)}
                disabled={isLocked}
                className={`px-3 py-1 text-xs font-medium rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  ((localChanges.text_align ?? textElement.text_align) || 'left') === align
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {align.charAt(0).toUpperCase() + align.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderImageControls = () => {
    if (!isImageElement) return null;
    
    const imageElement = element as ImageRegion;
    
    return (
      <div className="space-y-4">
        {/* Placeholder Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Placeholder Text</label>
          <input
            type="text"
            value={localChanges.placeholder_text ?? imageElement.placeholder_text}
            onChange={(e) => handleChange('placeholder_text', e.target.value)}
            disabled={isLocked}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Enter placeholder text..."
          />
        </div>
        
        {/* Image Fit */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Image Fit</label>
          <select
            value={(localChanges.fit ?? imageElement.fit) || 'cover'}
            onChange={(e) => handleChange('fit', e.target.value)}
            disabled={isLocked}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="cover">Cover</option>
            <option value="contain">Contain</option>
            <option value="fill">Fill</option>
            <option value="scale-down">Scale Down</option>
            <option value="none">None</option>
          </select>
        </div>
        
        {/* Border Radius */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Border Radius</label>
          <input
            type="number"
            value={(localChanges.border_radius ?? imageElement.border_radius) || 0}
            onChange={(e) => handleChange('border_radius', parseInt(e.target.value) || 0)}
            disabled={isLocked}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            min="0"
            max="50"
          />
        </div>
        
        {/* Background Color (for transparent images) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Background Color</label>
          <div className="flex items-center space-x-3">
            <ColorPicker
              color={localChanges.background_color ?? imageElement.background_color || '#ffffff'}
              onChange={(color) => handleChange('background_color', color)}
              disabled={isLocked}
            />
            <span className="text-sm text-gray-600 font-mono">
              {localChanges.background_color ?? imageElement.background_color || '#ffffff'}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderElementPreview = () => {
    if (!isVisible) return null;
    
    return (
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <h6 className="text-xs font-medium text-gray-700 mb-2">Preview</h6>
        <div className="bg-white border border-gray-200 rounded p-3 min-h-[60px] flex items-center justify-center">
          {isTextElement ? (
            <div
              style={{
                fontFamily: localChanges.font_family ?? (element as TextElement).font_family,
                fontSize: `${localChanges.font_size ?? (element as TextElement).font_size}px`,
                fontWeight: localChanges.font_weight ?? (element as TextElement).font_weight,
                color: localChanges.color ?? (element as TextElement).color,
                textAlign: localChanges.text_align ?? (element as TextElement).text_align || 'left'
              }}
              className="max-w-full"
            >
              {localChanges.text ?? (element as TextElement).text || 'Sample text'}
            </div>
          ) : (
            <div
              className="w-full h-16 border border-gray-300 rounded flex items-center justify-center text-xs text-gray-500"
              style={{
                borderRadius: `${localChanges.border_radius ?? (element as ImageRegion).border_radius || 0}px`,
                backgroundColor: localChanges.background_color ?? (element as ImageRegion).background_color || '#f3f4f6'
              }}
            >
              {localChanges.placeholder_text ?? (element as ImageRegion).placeholder_text || 'Image placeholder'}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {renderElementHeader()}
      
      {!isLocked && (
        <>
          {renderPositionControls()}
          {renderTextControls()}
          {renderImageControls()}
        </>
      )}
      
      {isLocked && (
        <div className="text-center py-8 text-gray-500">
          <Lock size={24} className="mx-auto mb-2" />
          <p className="text-sm">Element is locked</p>
          <p className="text-xs">Click the lock icon to unlock and edit</p>
        </div>
      )}
      
      {renderElementPreview()}
    </div>
  );
};

export default ElementEditor;