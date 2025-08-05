import React, { useState, useCallback } from 'react';
import { Toaster } from 'react-hot-toast';
import { Upload, Download, Palette, Type, Settings } from 'lucide-react';
import ImageUpload from './components/ImageUpload';
import TemplateEditor from './components/TemplateEditor';
import PreviewPanel from './components/PreviewPanel';
import FontManager from './components/FontManager';
import { AnalysisResult, TemplateData, FontInfo } from './types';
import './App.css';

interface AppState {
  currentStep: 'upload' | 'edit' | 'preview';
  analysisResult: AnalysisResult | null;
  templateData: TemplateData | null;
  previewUrl: string | null;
  fonts: FontInfo[];
  isLoading: boolean;
}

function App() {
  const [state, setState] = useState<AppState>({
    currentStep: 'upload',
    analysisResult: null,
    templateData: null,
    previewUrl: null,
    fonts: [],
    isLoading: false
  });

  const [showFontManager, setShowFontManager] = useState(false);

  const handleImageAnalyzed = useCallback((result: AnalysisResult) => {
    setState(prev => ({
      ...prev,
      analysisResult: result,
      currentStep: 'edit'
    }));
  }, []);

  const handleTemplateGenerated = useCallback((template: TemplateData) => {
    setState(prev => ({
      ...prev,
      templateData: template,
      currentStep: 'preview'
    }));
  }, []);

  const handlePreviewGenerated = useCallback((previewUrl: string) => {
    setState(prev => ({
      ...prev,
      previewUrl
    }));
  }, []);

  const handleFontsUpdated = useCallback((fonts: FontInfo[]) => {
    setState(prev => ({
      ...prev,
      fonts
    }));
  }, []);

  const resetToUpload = useCallback(() => {
    setState({
      currentStep: 'upload',
      analysisResult: null,
      templateData: null,
      previewUrl: null,
      fonts: state.fonts,
      isLoading: false
    });
  }, [state.fonts]);

  const renderStepIndicator = () => {
    const steps = [
      { key: 'upload', label: 'Upload Image', icon: Upload },
      { key: 'edit', label: 'Edit Template', icon: Settings },
      { key: 'preview', label: 'Preview & Download', icon: Download }
    ];

    return (
      <div className="flex items-center justify-center mb-8">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = state.currentStep === step.key;
          const isCompleted = steps.findIndex(s => s.key === state.currentStep) > index;
          
          return (
            <React.Fragment key={step.key}>
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-100 text-blue-700' 
                  : isCompleted 
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-500'
              }`}>
                <Icon size={20} />
                <span className="font-medium">{step.label}</span>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-8 h-0.5 mx-2 ${
                  isCompleted ? 'bg-green-300' : 'bg-gray-300'
                }`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  const renderCurrentStep = () => {
    switch (state.currentStep) {
      case 'upload':
        return (
          <ImageUpload 
            onImageAnalyzed={handleImageAnalyzed}
            isLoading={state.isLoading}
            onLoadingChange={(loading) => setState(prev => ({ ...prev, isLoading: loading }))}
          />
        );
      
      case 'edit':
        return (
          <TemplateEditor
            analysisResult={state.analysisResult!}
            fonts={state.fonts}
            onTemplateGenerated={handleTemplateGenerated}
            onBack={resetToUpload}
            isLoading={state.isLoading}
            onLoadingChange={(loading) => setState(prev => ({ ...prev, isLoading: loading }))}
          />
        );
      
      case 'preview':
        return (
          <PreviewPanel
            templateData={state.templateData!}
            previewUrl={state.previewUrl}
            onPreviewGenerated={handlePreviewGenerated}
            onBack={() => setState(prev => ({ ...prev, currentStep: 'edit' }))}
            onStartOver={resetToUpload}
            isLoading={state.isLoading}
            onLoadingChange={(loading) => setState(prev => ({ ...prev, isLoading: loading }))}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Palette className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">PinMaker</h1>
              <span className="text-sm text-gray-500">Pinterest Template Generator</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFontManager(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                <Type size={16} />
                <span>Manage Fonts</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderStepIndicator()}
        {renderCurrentStep()}
      </main>

      {/* Font Manager Modal */}
      {showFontManager && (
        <FontManager
          fonts={state.fonts}
          onFontsUpdated={handleFontsUpdated}
          onClose={() => setShowFontManager(false)}
        />
      )}
    </div>
  );
}

export default App;