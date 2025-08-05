import React, { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Download, RefreshCw, Share2, Settings, Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import { PreviewPanelProps, PreviewOptions } from '../types';
import { generatePreview, downloadTemplate, downloadPreview } from '../services/api';

const PreviewPanel: React.FC<PreviewPanelProps> = ({
  templateData,
  onBack,
  isLoading,
  onLoadingChange
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewOptions, setPreviewOptions] = useState<PreviewOptions>({
    sample_text: {
      title: 'Amazing Product',
      subtitle: 'Perfect for Your Needs',
      description: 'Discover the best solution for your lifestyle',
      cta: 'Shop Now',
      price: '$29.99',
      discount: '50% OFF'
    },
    stock_images: {
      keywords: ['product', 'lifestyle', 'modern'],
      style: 'modern',
      color_scheme: 'vibrant'
    },
    format: 'jpeg',
    quality: 90
  });
  const [showOptions, setShowOptions] = useState(false);
  const [previewHistory, setPreviewHistory] = useState<string[]>([]);

  const generateInitialPreview = useCallback(async () => {
    try {
      onLoadingChange(true);
      const preview = await generatePreview(templateData.id, previewOptions);
      setPreviewUrl(preview.preview_url);
      setPreviewHistory(prev => [preview.preview_url, ...prev.slice(0, 4)]);
      toast.success('Preview generated successfully!');
    } catch (error) {
      console.error('Preview generation failed:', error);
      toast.error('Failed to generate preview. Please try again.');
    } finally {
      onLoadingChange(false);
    }
  }, [templateData.id, previewOptions, onLoadingChange]);

  // Generate initial preview
  useEffect(() => {
    generateInitialPreview();
  }, [generateInitialPreview]);

  const regeneratePreview = async () => {
    try {
      onLoadingChange(true);
      const preview = await generatePreview(templateData.id, previewOptions);
      setPreviewUrl(preview.preview_url);
      setPreviewHistory(prev => [preview.preview_url, ...prev.slice(0, 4)]);
      toast.success('Preview regenerated!');
    } catch (error) {
      console.error('Preview regeneration failed:', error);
      toast.error('Failed to regenerate preview. Please try again.');
    } finally {
      onLoadingChange(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const blob = await downloadTemplate(templateData.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${templateData.metadata.name || 'template'}.svg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Template downloaded!');
    } catch (error) {
      console.error('Template download failed:', error);
      toast.error('Failed to download template.');
    }
  };

  const handleDownloadPreview = async () => {
    if (!previewUrl) return;
    
    try {
      const blob = await downloadPreview(templateData.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${templateData.metadata.name || 'preview'}.${previewOptions.format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Preview downloaded!');
    } catch (error) {
      console.error('Preview download failed:', error);
      toast.error('Failed to download preview.');
    }
  };

  const handleSharePreview = async () => {
    if (!previewUrl) return;

    try {
      await navigator.share({
        title: 'Pinterest Template Preview',
        text: 'Check out this Pinterest template!',
        url: previewUrl
      });
    } catch (error) {
      // Fallback to clipboard
      try {
        await navigator.clipboard.writeText(previewUrl);
        toast.success('Preview URL copied to clipboard!');
      } catch (clipboardError) {
        toast.error('Failed to share preview.');
      }
    }
  };

  const updatePreviewOptions = useCallback((updates: Partial<PreviewOptions>) => {
    setPreviewOptions(prev => ({ ...prev, ...updates }));
  }, []);

  const renderToolbar = () => (
    <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
      <div className="flex items-center space-x-4">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft size={16} />
          <span>Back to Editor</span>
        </button>

        <div className="h-6 w-px bg-gray-300" />

        <h2 className="text-lg font-semibold text-gray-900">
          Preview: {templateData.metadata.name || 'Untitled Template'}
        </h2>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={() => setShowOptions(!showOptions)}
          className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
            showOptions
              ? 'bg-blue-100 text-blue-700'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <Settings size={16} />
          <span>Options</span>
        </button>

        <button
          onClick={regeneratePreview}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          <span>Regenerate</span>
        </button>

        <button
          onClick={handleSharePreview}
          disabled={!previewUrl}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Share2 size={16} />
          <span>Share</span>
        </button>

        <button
          onClick={handleDownloadTemplate}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Download size={16} />
          <span>Download SVG</span>
        </button>

        <button
          onClick={handleDownloadPreview}
          disabled={!previewUrl}
          className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download size={16} />
          <span>Download Preview</span>
        </button>
      </div>
    </div>
  );

  const renderOptionsPanel = () => {
    if (!showOptions) return null;

    return (
      <div className="bg-gray-50 border-b border-gray-200 p-4">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Preview Options</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Sample Text Options */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">Sample Text</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
                  <input
                    type="text"
                    value={previewOptions.sample_text.title}
                    onChange={(e) => updatePreviewOptions({
                      sample_text: { ...previewOptions.sample_text, title: e.target.value }
                    })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Subtitle</label>
                  <input
                    type="text"
                    value={previewOptions.sample_text.subtitle}
                    onChange={(e) => updatePreviewOptions({
                      sample_text: { ...previewOptions.sample_text, subtitle: e.target.value }
                    })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Call to Action</label>
                  <input
                    type="text"
                    value={previewOptions.sample_text.cta}
                    onChange={(e) => updatePreviewOptions({
                      sample_text: { ...previewOptions.sample_text, cta: e.target.value }
                    })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Stock Image Options */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">Stock Images</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Keywords</label>
                  <input
                    type="text"
                    value={previewOptions.stock_images.keywords.join(', ')}
                    onChange={(e) => updatePreviewOptions({
                      stock_images: {
                        ...previewOptions.stock_images,
                        keywords: e.target.value.split(',').map(k => k.trim()).filter(Boolean)
                      }
                    })}
                    placeholder="product, lifestyle, modern"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Style</label>
                  <select
                    value={previewOptions.stock_images.style}
                    onChange={(e) => updatePreviewOptions({
                      stock_images: { ...previewOptions.stock_images, style: e.target.value }
                    })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="modern">Modern</option>
                    <option value="vintage">Vintage</option>
                    <option value="minimal">Minimal</option>
                    <option value="bold">Bold</option>
                    <option value="elegant">Elegant</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Color Scheme</label>
                  <select
                    value={previewOptions.stock_images.color_scheme}
                    onChange={(e) => updatePreviewOptions({
                      stock_images: { ...previewOptions.stock_images, color_scheme: e.target.value }
                    })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="vibrant">Vibrant</option>
                    <option value="muted">Muted</option>
                    <option value="monochrome">Monochrome</option>
                    <option value="warm">Warm</option>
                    <option value="cool">Cool</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Export Options */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">Export Settings</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Format</label>
                  <select
                    value={previewOptions.format}
                    onChange={(e) => updatePreviewOptions({ format: e.target.value as 'jpeg' | 'png' })}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="jpeg">JPEG</option>
                    <option value="png">PNG</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Quality ({previewOptions.quality}%)</label>
                  <input
                    type="range"
                    min="60"
                    max="100"
                    value={previewOptions.quality}
                    onChange={(e) => updatePreviewOptions({ quality: parseInt(e.target.value) })}
                    className="w-full"
                  />
                </div>
                
                <button
                  onClick={regeneratePreview}
                  disabled={isLoading}
                  className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                  <span>Apply Changes</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderPreviewContent = () => {
    if (isLoading) {
      return (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-300 rounded-full animate-pulse mx-auto mb-4" />
            <p className="text-gray-600">Generating preview...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="flex-1 bg-gray-50 p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Main Preview */}
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Preview</h3>
                <div className="text-sm text-gray-500">
                  {templateData.metadata.width} × {templateData.metadata.height}px
                </div>
              </div>
              
              {previewUrl ? (
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <img
                    src={previewUrl}
                    alt="Template Preview"
                    className="w-full h-auto max-w-2xl mx-auto block"
                    style={{ maxHeight: '600px', objectFit: 'contain' }}
                  />
                </div>
              ) : (
                <div className="border border-gray-200 rounded-lg p-12 text-center">
                  <div className="text-gray-400 mb-2">
                    <Eye size={48} className="mx-auto" />
                  </div>
                  <p className="text-gray-600">No preview available</p>
                  <button
                    onClick={regeneratePreview}
                    className="mt-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Generate Preview
                  </button>
                </div>
              )}
            </div>

            {/* Preview History */}
            {previewHistory.length > 1 && (
              <div className="border-t border-gray-200 p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Previews</h4>
                <div className="flex space-x-3 overflow-x-auto">
                  {previewHistory.slice(1).map((url, index) => (
                    <button
                      key={index}
                      onClick={() => setPreviewUrl(url)}
                      className="flex-shrink-0 w-20 h-20 border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors"
                    >
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Template Info */}
            <div className="border-t border-gray-200 p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="font-medium text-gray-900">Template ID</div>
                  <div className="text-gray-600 font-mono text-xs">{templateData.id}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="font-medium text-gray-900">Created</div>
                  <div className="text-gray-600">{new Date(templateData.metadata.created_at).toLocaleDateString()}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="font-medium text-gray-900">Placeholders</div>
                  <div className="text-gray-600">
                    {templateData.placeholders.text.length + templateData.placeholders.images.length} total
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="font-medium text-gray-900">Format</div>
                  <div className="text-gray-600">SVG + {previewOptions.format.toUpperCase()}</div>
                </div>
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
      {renderOptionsPanel()}
      {renderPreviewContent()}
    </div>
  );
};

export default PreviewPanel;