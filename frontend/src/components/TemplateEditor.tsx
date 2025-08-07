import React, { useState } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

interface AnalysisResult {
  dominant_colors: string[];
  style_suggestions: string[];
  text_suggestions: string[];
  mood: string;
}

interface TemplateData {
  template_url: string;
  style: string;
  colors: string[];
  text: string;
}

interface TemplateEditorProps {
  uploadedImage: string;
  analysisResult: AnalysisResult;
  onTemplateGenerated: (templateData: TemplateData) => void;
}

const TemplateEditor: React.FC<TemplateEditorProps> = ({
  uploadedImage,
  analysisResult,
  onTemplateGenerated
}) => {
  const [selectedStyle, setSelectedStyle] = useState('modern');
  const [customText, setCustomText] = useState('');
  const [selectedColors, setSelectedColors] = useState<string[]>(analysisResult.dominant_colors.slice(0, 2));
  const [isGenerating, setIsGenerating] = useState(false);
  const [customColor, setCustomColor] = useState('#000000');

  const templateStyles = [
    { id: 'modern', name: 'Modern', description: 'Clean and minimalist' },
    { id: 'vintage', name: 'Vintage', description: 'Retro and classic' },
    { id: 'bold', name: 'Bold', description: 'High contrast and striking' },
    { id: 'elegant', name: 'Elegant', description: 'Sophisticated and refined' }
  ];

  const predefinedColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
    '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
  ];

  const handleColorSelect = (color: string) => {
    if (selectedColors.includes(color)) {
      setSelectedColors(selectedColors.filter(c => c !== color));
    } else if (selectedColors.length < 3) {
      setSelectedColors([...selectedColors, color]);
    }
  };

  const handleCustomColorAdd = () => {
    if (!selectedColors.includes(customColor) && selectedColors.length < 3) {
      setSelectedColors([...selectedColors, customColor]);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setCustomText(suggestion);
  };

  const generateTemplate = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post(API_ENDPOINTS.GENERATE_TEMPLATE, {
        image_url: uploadedImage,
        style: selectedStyle,
        text: customText,
        colors: selectedColors,
        analysis: analysisResult
      });

      const templateData: TemplateData = {
        template_url: response.data.template_url,
        style: selectedStyle,
        colors: selectedColors,
        text: customText
      };

      onTemplateGenerated(templateData);
    } catch (error) {
      console.error('Error generating template:', error);
      alert('Failed to generate template. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="template-editor">
      <div className="editor-content">
        <div className="original-image">
          <h3>Original Image</h3>
          <img src={uploadedImage} alt="Uploaded" className="preview-image" />
          
          <div className="analysis-info">
            <h3>AI Analysis</h3>
            <div className="analysis-details">
              <p><strong>Mood:</strong> {analysisResult.mood}</p>
              <p><strong>Dominant Colors:</strong></p>
              <div className="color-options">
                {analysisResult.dominant_colors.map((color, index) => (
                  <div
                    key={index}
                    className="color-swatch"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
              <div className="style-recommendations">
                <p><strong>Style Recommendations:</strong></p>
                <ul>
                  {analysisResult.style_suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="editor-controls">
          <div className="control-group">
            <label>Template Style</label>
            <div className="template-options">
              {templateStyles.map(style => (
                <div
                  key={style.id}
                  className={`template-option ${selectedStyle === style.id ? 'selected' : ''}`}
                  onClick={() => setSelectedStyle(style.id)}
                >
                  <h4>{style.name}</h4>
                  <p>{style.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label htmlFor="custom-text">Custom Text</label>
            <textarea
              id="custom-text"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder="Enter your Pinterest caption or quote..."
            />
            
            <div className="text-suggestions">
              <p>AI Suggestions:</p>
              {analysisResult.text_suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Color Scheme (Select up to 3)</label>
            <div className="color-options">
              {/* Dominant colors from analysis */}
              {analysisResult.dominant_colors.map((color, index) => (
                <div
                  key={`dominant-${index}`}
                  className={`color-option ${selectedColors.includes(color) ? 'selected' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorSelect(color)}
                  title={`Dominant color: ${color}`}
                />
              ))}
              
              {/* Predefined colors */}
              {predefinedColors.map((color, index) => (
                <div
                  key={`predefined-${index}`}
                  className={`color-option ${selectedColors.includes(color) ? 'selected' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorSelect(color)}
                  title={color}
                />
              ))}
              
              {/* Custom color picker */}
              <input
                type="color"
                value={customColor}
                onChange={(e) => setCustomColor(e.target.value)}
                className="custom-color-picker"
                title="Custom color"
              />
              <button
                onClick={handleCustomColorAdd}
                disabled={selectedColors.length >= 3 || selectedColors.includes(customColor)}
                style={{ marginLeft: '0.5rem', padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
              >
                Add
              </button>
            </div>
            
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
              Selected: {selectedColors.length}/3 colors
            </div>
          </div>

          <button
            className="generate-btn"
            onClick={generateTemplate}
            disabled={isGenerating || !customText.trim()}
          >
            {isGenerating ? 'Generating...' : 'Generate Template'}
          </button>
        </div>

        <div className="template-preview">
          <h3>Preview</h3>
          <div style={{ 
            width: '200px', 
            height: '300px', 
            border: '2px dashed #ccc', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            margin: '0 auto',
            borderRadius: '8px',
            background: '#f9f9f9'
          }}>
            {isGenerating ? (
              <div className="spinner" />
            ) : (
              <p style={{ color: '#666', textAlign: 'center' }}>
                Template preview will appear here after generation
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor;