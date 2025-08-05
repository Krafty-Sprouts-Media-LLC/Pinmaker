import React, { useState, useCallback } from 'react';
import { Upload, X, Trash2, Eye, EyeOff, Type, AlertCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { FontManagerProps, FontInfo, FontUploadResult } from '../types';
import { uploadFont, deleteFont, getFontInfo } from '../services/api';

const FontManager: React.FC<FontManagerProps> = ({
  fonts,
  onFontsUpdate,
  onClose
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [previewText, setPreviewText] = useState('The quick brown fox jumps over the lazy dog');
  const [showPreviews, setShowPreviews] = useState(true);
  const [selectedFont, setSelectedFont] = useState<FontInfo | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const fontFiles = acceptedFiles.filter(file => 
      file.type.includes('font') || 
      file.name.match(/\.(ttf|otf|woff|woff2)$/i)
    );

    if (fontFiles.length === 0) {
      toast.error('Please select valid font files (.ttf, .otf, .woff, .woff2)');
      return;
    }

    setUploading(true);
    const results: FontUploadResult[] = [];

    for (const file of fontFiles) {
      try {
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
        
        const result = await uploadFont(file, (progress) => {
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
        });
        
        results.push(result);
        setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
        
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    setUploading(false);
    setUploadProgress({});
    
    if (results.length > 0) {
      toast.success(`Successfully uploaded ${results.length} font(s)`);
      onFontsUpdate();
    }
  }, [onFontsUpdate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'font/ttf': ['.ttf'],
      'font/otf': ['.otf'],
      'font/woff': ['.woff'],
      'font/woff2': ['.woff2']
    },
    multiple: true,
    disabled: uploading
  });

  const handleDeleteFont = async (fontId: string) => {
    if (!window.confirm('Are you sure you want to delete this font?')) {
      return;
    }

    try {
      await deleteFont(fontId);
      toast.success('Font deleted successfully');
      onFontsUpdate();
      if (selectedFont?.id === fontId) {
        setSelectedFont(null);
      }
    } catch (error) {
      console.error('Failed to delete font:', error);
      toast.error('Failed to delete font');
    }
  };

  const handleFontSelect = async (font: FontInfo) => {
    if (font.type === 'web-safe') {
      setSelectedFont(font);
      return;
    }

    try {
      const fontInfo = await getFontInfo(font.id);
      setSelectedFont(fontInfo);
    } catch (error) {
      console.error('Failed to get font info:', error);
      toast.error('Failed to load font details');
    }
  };

  const renderUploadArea = () => (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Custom Fonts</h3>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : uploading
            ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50 cursor-pointer'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-3">
          <div className={`p-3 rounded-full ${
            isDragActive ? 'bg-blue-100' : 'bg-gray-100'
          }`}>
            <Upload size={24} className={isDragActive ? 'text-blue-600' : 'text-gray-600'} />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive ? 'Drop font files here' : 'Upload font files'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Drag & drop or click to select TTF, OTF, WOFF, or WOFF2 files
            </p>
          </div>
          
          {uploading && (
            <div className="w-full max-w-xs">
              <div className="text-sm text-gray-600 mb-2">Uploading fonts...</div>
              {Object.entries(uploadProgress).map(([filename, progress]) => (
                <div key={filename} className="mb-2">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span className="truncate">{filename}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <div className="flex items-start space-x-2">
          <AlertCircle size={16} className="text-amber-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-amber-700">Font Upload Guidelines:</p>
            <ul className="mt-1 space-y-1 text-gray-600">
              <li>• Supported formats: TTF, OTF, WOFF, WOFF2</li>
              <li>• Maximum file size: 10MB per font</li>
              <li>• Ensure you have proper licensing for commercial use</li>
              <li>• Font names should be unique to avoid conflicts</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFontList = () => {
    const webSafeFonts = fonts.filter(font => font.type === 'web-safe');
    const uploadedFonts = fonts.filter(font => font.type === 'uploaded');

    return (
      <div className="space-y-6">
        {/* Preview Controls */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Available Fonts</h3>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowPreviews(!showPreviews)}
              className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {showPreviews ? <EyeOff size={16} /> : <Eye size={16} />}
              <span>{showPreviews ? 'Hide' : 'Show'} Previews</span>
            </button>
          </div>
        </div>

        {showPreviews && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preview Text
            </label>
            <input
              type="text"
              value={previewText}
              onChange={(e) => setPreviewText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter text to preview fonts..."
            />
          </div>
        )}

        {/* Uploaded Fonts */}
        {uploadedFonts.length > 0 && (
          <div>
            <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center space-x-2">
              <Upload size={16} />
              <span>Custom Fonts ({uploadedFonts.length})</span>
            </h4>
            
            <div className="grid grid-cols-1 gap-3">
              {uploadedFonts.map((font) => (
                <div
                  key={font.id}
                  className={`border rounded-lg p-4 transition-all cursor-pointer ${
                    selectedFont?.id === font.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                  onClick={() => handleFontSelect(font)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <Type size={16} className="text-gray-600" />
                        <div>
                          <h5 className="font-medium text-gray-900">{font.family}</h5>
                          <p className="text-sm text-gray-600">
                            {font.variants?.join(', ') || 'Regular'} • {font.format || 'Unknown format'}
                          </p>
                        </div>
                      </div>
                      
                      {showPreviews && (
                        <div className="mt-3">
                          <div
                            className="text-lg text-gray-800"
                            style={{ fontFamily: font.family }}
                          >
                            {previewText}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteFont(font.id);
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete font"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Web Safe Fonts */}
        <div>
          <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center space-x-2">
            <Type size={16} />
            <span>Web Safe Fonts ({webSafeFonts.length})</span>
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {webSafeFonts.map((font) => (
              <div
                key={font.id}
                className={`border rounded-lg p-4 transition-all cursor-pointer ${
                  selectedFont?.id === font.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
                onClick={() => handleFontSelect(font)}
              >
                <div className="flex items-center space-x-3">
                  <Type size={16} className="text-gray-600" />
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">{font.family}</h5>
                    <p className="text-sm text-gray-600">
                      {font.variants?.join(', ') || 'Regular'}
                    </p>
                  </div>
                </div>
                
                {showPreviews && (
                  <div className="mt-3">
                    <div
                      className="text-lg text-gray-800"
                      style={{ fontFamily: font.family }}
                    >
                      {previewText}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderFontDetails = () => {
    if (!selectedFont) return null;

    return (
      <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Font Details</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Font Family</label>
              <p className="text-gray-900">{selectedFont.family}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <p className="text-gray-900 capitalize">{selectedFont.type}</p>
            </div>
            
            {selectedFont.variants && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Variants</label>
                <div className="flex flex-wrap gap-2">
                  {selectedFont.variants.map((variant) => (
                    <span
                      key={variant}
                      className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded"
                    >
                      {variant}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {selectedFont.format && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                <p className="text-gray-900 uppercase">{selectedFont.format}</p>
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Font Preview</label>
            <div className="space-y-3">
              {['12px', '16px', '24px', '32px'].map((size) => (
                <div key={size}>
                  <div className="text-xs text-gray-500 mb-1">{size}</div>
                  <div
                    className="text-gray-900"
                    style={{ 
                      fontFamily: selectedFont.family,
                      fontSize: size
                    }}
                  >
                    {previewText}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Font Manager</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {renderUploadArea()}
          {renderFontList()}
          {renderFontDetails()}
        </div>
        
        {/* Footer */}
        <div className="border-t border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {fonts.length} fonts available • {fonts.filter(f => f.type === 'uploaded').length} custom fonts
            </div>
            
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FontManager;