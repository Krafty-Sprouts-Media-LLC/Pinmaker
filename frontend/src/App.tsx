import React, { useState } from 'react';
import './App.css';
import ImageUploader from './components/ImageUploader';
import TemplateEditor from './components/TemplateEditor';
import TemplateExporter from './components/TemplateExporter';

interface AnalysisResult {
  colors: Array<{type: string; color: string; index?: number}>;
  dominant_colors?: string[]; // Keep for backward compatibility
  style_suggestions: string[];
  text_suggestions: string[];
  mood: string;
  fonts: any[];
  text_elements: any[];
  image_regions: any[];
  layout_structure: any;
  background_info: any;
}

function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [templateData, setTemplateData] = useState<any>(null);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Pinterest Template Generator</h1>
        <p>Upload an image, analyze it, and create beautiful Pinterest templates</p>
      </header>
      
      <main className="App-main">
        <div className="workflow-container">
          <div className="step">
            <h2>Step 1: Upload Image</h2>
            <ImageUploader 
              onImageUpload={setUploadedImage}
              onAnalysisComplete={setAnalysisResult}
            />
          </div>
          
          {uploadedImage && analysisResult && (
            <div className="step">
              <h2>Step 2: Edit Template</h2>
              <TemplateEditor
                uploadedImage={uploadedImage}
                analysisResult={analysisResult}
                onTemplateGenerated={setTemplateData}
              />
            </div>
          )}
          
          {templateData && (
            <div className="step">
              <h2>Step 3: Export Template</h2>
              <TemplateExporter templateData={templateData} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
