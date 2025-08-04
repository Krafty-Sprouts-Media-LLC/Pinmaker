import React, { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Save, Download, Palette, Type, Move, RotateCcw, Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import { TemplateEditorProps, TemplateData, TemplateUpdate, TextElement, ImageRegion, FontInfo } from '../types';
import { generateTemplate, updateTemplate } from '../services/api';
import ColorPicker from './ColorPicker';
import FontSelector from './FontSelector';
import ElementEditor from './ElementEditor';

const TemplateEditor: React.FC<TemplateEditorProps> = ({
  analysisResult,
  fonts,
  onTemplateGenerated,
  onBack,
  isLoading,
  onLoadingChange
}) => {
  const [templateData, setTemplateData] = useState<TemplateData | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<'select' | 'color' | 'font' | 'position'>('select');
  const [modifications, setModifications] = useState<TemplateUpdate>({});
  const [previewMode, setPreviewMode] = useState(false);

  // Generate initial template from analysis
  useEffect(() => {
    const generateInitialTemplate = async () => {
      try {
        onLoadingChange(true);
        const template = await generateTemplate(analysisResult.id);
        setTemplateData(template);
        toast.success('Template generated successfully!');
      } catch (error) {
        console.error('Template generation failed:', error);
        toast.error('Failed to generate template. Please try again.');
      } finally {
        onLoadingChange(false);
      }
    };

    generateInitialTemplate();
  }, [analysisResult.id, onLoadingChange]);

  const handleElementSelect = useCallback((elementId: string) => {
    setSelectedElement(elementId);
    setEditMode('select');
  }, []);

  const handleColorChange = useCallback((elementId: string, color: string) => {
    const newModifications = {
      ...modifications,
      colors: {
        ...modifications.colors,
        [elementId]: color
      }
    };
    setModifications(newModifications);
  }, [modifications]);

  const handleFontChange = useCallback((elementId: string, fontFamily: string, fontSize?: number, fontWeight?: string) => {
    const newModifications = {
      ...modifications,
      fonts: {
        ...modifications.fonts,
        [elementId]: {
          family: fontFamily,
          ...(fontSize && { size: fontSize }),
          ...(fontWeight && { weight: fontWeight })
        }
      }
    };
    setModifications(newModifications);
  }, [modifications]);

  const handlePositionChange = useCallback((elementId: string, x: number, y: number, width?: number, height?: number) => {
    const newModifications = {
      ...modifications,
      positions: {
        ...modifications.positions,
        [elementId]: {
          x,
          y,
          ...(width && { width }),
          ...(height && { height })
        }
      }
    };
    setModifications(newModifications);
  }, [modifications]);

  const handleContentChange = useCallback((elementId: string, content: string) => {
    const newModifications = {
      ...modifications,
      content: {
        ...modifications.content,
        text: {
          ...modifications.content?.text,
          [elementId]: content
        }
      }
    };
    setModifications(newModifications);
  }, [modifications]);

  const applyModifications = async () => {
    if (!templateData || Object.keys(modifications).length === 0) {
      toast.info('No changes to apply');
      return;
    }

    try {
      onLoadingChange(true);
      const updatedTemplate = await updateTemplate(templateData.id, modifications);
      setTemplateData(updatedTemplate);
      toast.success('Template updated successfully!');
    } catch (error) {
      console.error('Template update failed:', error);
      toast.error('Failed to update template. Please try again.');
    } finally {
      onLoadingChange(false);
    }
  };

  const resetModifications = () => {
    setModifications({});
    setSelectedElement(null);
    toast.info('Changes reset to original design');
  };

  const proceedToPreview = () => {
    if (!templateData) return;
    onTemplateGenerated(templateData);
  };

  const renderToolbar = () => {
    const tools = [
      { key: 'select', label: 'Select', icon: Move },
      { key: 'color', label: 'Colors', icon: Palette },
      { key: 'font', label: 'Fonts', icon: Type },
    ];

    return (
      <div className="flex items-center space-x-2 p-4 bg-white border-b border-gray-200">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft size={16} />
          <span>Back</span>
        </button>

        <div className="flex items-center space-x-1 ml-4">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <button
                key={tool.key}
                onClick={() => setEditMode(tool.key as any)}
                className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  editMode === tool.key
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={16} />
                <span>{tool.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex-1" />

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
              previewMode
                ? 'bg-green-100 text-green-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Eye size={16} />
            <span>{previewMode ? 'Edit Mode' : 'Preview'}</span>
          </button>

          <button
            onClick={resetModifications}
            disabled={Object.keys(modifications).length === 0}
            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RotateCcw size={16} />
            <span>Reset</span>
          </button>

          <button
            onClick={applyModifications}
            disabled={Object.keys(modifications).length === 0 || isLoading}
            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={16} />
            <span>Apply Changes</span>
          </button>

          <button
            onClick={proceedToPreview}
            disabled={!templateData || isLoading}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download size={16} />
            <span>Generate Preview</span>
          </button>
        </div>
      </div>
    );
  };

  const renderPropertyPanel = () => {
    if (!selectedElement || !templateData) return null;

    const element = [
      ...templateData.editable_elements.text_elements,
      ...templateData.editable_elements.image_regions
    ].find(el => el.id === selectedElement);

    if (!element) return null;

    return (
      <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Edit {element.id.includes('text') ? 'Text' : 'Image'} Element
        </h3>

        <ElementEditor
          element={element}
          fonts={fonts}
          onUpdate={(updates) => {
            if ('color' in updates) {
              handleColorChange(selectedElement, updates.color as string);
            }
            if ('font_family' in updates) {
              handleFontChange(
                selectedElement,
                updates.font_family as string,
                updates.font_size as number,
                updates.font_weight as string
              );
            }
            if ('x' in updates || 'y' in updates) {
              handlePositionChange(
                selectedElement,
                updates.x as number,
                updates.y as number,
                updates.width as number,
                updates.height as number
              );
            }
            if ('text' in updates) {
              handleContentChange(selectedElement, updates.text as string);
            }
          }}
          onDelete={() => {
            // Handle element deletion
            setSelectedElement(null);
          }}
        />
      </div>
    );
  };

  const renderCanvas = () => {
    if (!templateData) {
      return (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-300 rounded-full animate-pulse mx-auto mb-4" />
            <p className="text-gray-600">Generating template...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="flex-1 bg-gray-50 p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Template Editor
              </h3>
              <div className="text-sm text-gray-500">
                {templateData.metadata.width} × {templateData.metadata.height}px
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="relative bg-white"
                style={{
                  width: '100%',
                  maxWidth: '600px',
                  aspectRatio: `${templateData.metadata.width} / ${templateData.metadata.height}`,
                  margin: '0 auto'
                }}
              >
                {/* SVG Template Display */}
                <div 
                  className="w-full h-full"
                  dangerouslySetInnerHTML={{ __html: templateData.svg_content }}
                />

                {/* Interactive Overlays */}
                {!previewMode && (
                  <>
                    {/* Text Element Overlays */}
                    {templateData.editable_elements.text_elements.map((element) => (
                      <div
                        key={element.id}
                        className={`absolute border-2 cursor-pointer transition-all ${
                          selectedElement === element.id
                            ? 'border-blue-500 bg-blue-100 bg-opacity-20'
                            : 'border-transparent hover:border-blue-300'
                        }`}
                        style={{
                          left: `${(element.x / templateData.metadata.width) * 100}%`,
                          top: `${(element.y / templateData.metadata.height) * 100}%`,
                          width: `${(element.width / templateData.metadata.width) * 100}%`,
                          height: `${(element.height / templateData.metadata.height) * 100}%`,
                        }}
                        onClick={() => handleElementSelect(element.id)}
                      />
                    ))}

                    {/* Image Element Overlays */}
                    {templateData.editable_elements.image_regions.map((element) => (
                      <div
                        key={element.id}
                        className={`absolute border-2 cursor-pointer transition-all ${
                          selectedElement === element.id
                            ? 'border-green-500 bg-green-100 bg-opacity-20'
                            : 'border-transparent hover:border-green-300'
                        }`}
                        style={{
                          left: `${(element.x / templateData.metadata.width) * 100}%`,
                          top: `${(element.y / templateData.metadata.height) * 100}%`,
                          width: `${(element.width / templateData.metadata.width) * 100}%`,
                          height: `${(element.height / templateData.metadata.height) * 100}%`,
                        }}
                        onClick={() => handleElementSelect(element.id)}
                      />
                    ))}
                  </>
                )}
              </div>
            </div>

            {/* Template Info */}
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="font-medium text-gray-900">Text Elements</div>
                <div className="text-gray-600">{templateData.editable_elements.text_elements.length}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="font-medium text-gray-900">Image Regions</div>
                <div className="text-gray-600">{templateData.editable_elements.image_regions.length}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="font-medium text-gray-900">Text Placeholders</div>
                <div className="text-gray-600">{templateData.placeholders.text.length}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="font-medium text-gray-900">Image Placeholders</div>
                <div className="text-gray-600">{templateData.placeholders.images.length}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col">
      {renderToolbar()}
      
      <div className="flex-1 flex overflow-hidden">
        {renderCanvas()}
        {selectedElement && renderPropertyPanel()}
      </div>
    </div>
  );
};

export default TemplateEditor;