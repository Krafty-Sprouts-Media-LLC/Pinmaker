import React, { useState } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

interface TemplateData {
  template_style: string;
  custom_text: string;
  color_scheme: string;
  preview_url: string;
  download_url?: string;
}

interface TemplateExporterProps {
  templateData: TemplateData;
}

const TemplateExporter: React.FC<TemplateExporterProps> = ({ templateData }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'png' | 'jpg'>('png');
  const [exportSize, setExportSize] = useState<'pinterest' | 'square' | 'story'>('pinterest');
  const [error, setError] = useState<string | null>(null);

  const sizeOptions = {
    pinterest: { width: 1000, height: 1500, label: 'Pinterest (1000x1500)' },
    square: { width: 1080, height: 1080, label: 'Square (1080x1080)' },
    story: { width: 1080, height: 1920, label: 'Story (1080x1920)' }
  };

  const handleDownload = async () => {
    setIsExporting(true);
    setError(null);

    try {
      const response = await axios.post(API_ENDPOINTS.EXPORT, {
        template_data: templateData,
        format: exportFormat,
        size: exportSize,
        dimensions: sizeOptions[exportSize]
      }, {
        responseType: 'blob'
      });

      // Create download link
      const blob = new Blob([response.data], { type: `image/${exportFormat}` });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pinterest-template-${Date.now()}.${exportFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export template');
      console.error('Export error:', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share && templateData.preview_url) {
      try {
        await navigator.share({
          title: 'My Pinterest Template',
          text: 'Check out this Pinterest template I created!',
          url: templateData.preview_url
        });
      } catch (err) {
        console.log('Share cancelled or failed:', err);
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(templateData.preview_url);
        alert('Preview URL copied to clipboard!');
      } catch (err) {
        console.error('Failed to copy to clipboard:', err);
      }
    }
  };

  const copyToClipboard = async () => {
    try {
      // Convert image to canvas and copy to clipboard
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = async () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        canvas.toBlob(async (blob) => {
          if (blob && navigator.clipboard) {
            try {
              await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
              ]);
              alert('Template copied to clipboard!');
            } catch (err) {
              console.error('Failed to copy image to clipboard:', err);
            }
          }
        });
      };
      img.src = templateData.preview_url;
    } catch (err) {
      console.error('Failed to copy image:', err);
    }
  };

  return (
    <div className="template-exporter">
      <div className="export-preview">
        <h3>Final Template</h3>
        <img 
          src={templateData.preview_url} 
          alt="Final Template" 
          className="final-preview"
        />
      </div>

      <div className="export-options">
        <h3>Export Options</h3>
        
        <div className="option-group">
          <label>Format:</label>
          <div className="format-options">
            <label className="radio-option">
              <input
                type="radio"
                value="png"
                checked={exportFormat === 'png'}
                onChange={(e) => setExportFormat(e.target.value as 'png')}
              />
              PNG (Best Quality)
            </label>
            <label className="radio-option">
              <input
                type="radio"
                value="jpg"
                checked={exportFormat === 'jpg'}
                onChange={(e) => setExportFormat(e.target.value as 'jpg')}
              />
              JPG (Smaller Size)
            </label>
          </div>
        </div>

        <div className="option-group">
          <label>Size:</label>
          <div className="size-options">
            {Object.entries(sizeOptions).map(([key, option]) => (
              <label key={key} className="radio-option">
                <input
                  type="radio"
                  value={key}
                  checked={exportSize === key}
                  onChange={(e) => setExportSize(e.target.value as any)}
                />
                {option.label}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="export-actions">
        <button 
          className="download-btn primary"
          onClick={handleDownload}
          disabled={isExporting}
        >
          {isExporting ? 'Exporting...' : `Download ${exportFormat.toUpperCase()}`}
        </button>
        
        <button 
          className="copy-btn secondary"
          onClick={copyToClipboard}
        >
          📋 Copy to Clipboard
        </button>
        
        <button 
          className="share-btn secondary"
          onClick={handleShare}
        >
          🔗 Share
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      <div className="template-info">
        <h4>Template Details</h4>
        <div className="info-grid">
          <div className="info-item">
            <span className="label">Style:</span>
            <span className="value">{templateData.template_style.replace('_', ' ')}</span>
          </div>
          <div className="info-item">
            <span className="label">Text:</span>
            <span className="value">{templateData.custom_text}</span>
          </div>
          <div className="info-item">
            <span className="label">Color:</span>
            <span 
              className="color-swatch"
              style={{ backgroundColor: templateData.color_scheme }}
            ></span>
            <span className="value">{templateData.color_scheme}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateExporter;