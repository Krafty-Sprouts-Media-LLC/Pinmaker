import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import { ImageUploadProps, AnalysisResult, SUPPORTED_IMAGE_FORMATS, MAX_FILE_SIZE } from '../types';
import { analyzeImage } from '../services/api';

const ImageUpload: React.FC<ImageUploadProps> = ({ 
  onImageAnalyzed, 
  isLoading, 
  onLoadingChange 
}) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      toast.error(`File size must be less than ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
      return;
    }

    // Validate file type
    if (!SUPPORTED_IMAGE_FORMATS.includes(file.type as any)) {
      toast.error('Please upload a JPEG, PNG, or WebP image');
      return;
    }

    setUploadedFile(file);
    
    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    // Start analysis
    await handleAnalyzeImage(file);
  }, []);

  const handleAnalyzeImage = async (file: File) => {
    try {
      onLoadingChange(true);
      setAnalysisProgress('Uploading image...');

      const result = await analyzeImage(file, (progress) => {
        if (progress < 30) {
          setAnalysisProgress('Uploading image...');
        } else if (progress < 60) {
          setAnalysisProgress('Analyzing colors and layout...');
        } else if (progress < 80) {
          setAnalysisProgress('Detecting text and fonts...');
        } else {
          setAnalysisProgress('Finalizing analysis...');
        }
      });

      setAnalysisProgress('Analysis complete!');
      toast.success('Image analyzed successfully!');
      onImageAnalyzed(result);
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('Failed to analyze image. Please try again.');
      setAnalysisProgress('');
    } finally {
      onLoadingChange(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: isLoading
  });

  const resetUpload = () => {
    setUploadedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setAnalysisProgress('');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your Pinterest Template
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload an image of a Pinterest template you'd like to recreate. Our AI will analyze the layout, 
          colors, fonts, and structure to generate an editable template.
        </p>
      </div>

      {!uploadedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 cursor-pointer ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-white" />
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {isDragActive ? 'Drop your image here' : 'Choose an image to upload'}
              </h3>
              <p className="text-gray-600 mb-4">
                Drag and drop your Pinterest template image, or click to browse
              </p>
              
              <div className="text-sm text-gray-500 space-y-1">
                <p>Supported formats: JPEG, PNG, WebP</p>
                <p>Maximum file size: {MAX_FILE_SIZE / (1024 * 1024)}MB</p>
              </div>
            </div>
            
            <button
              type="button"
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 transform hover:scale-105"
              disabled={isLoading}
            >
              Select Image
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Image Preview */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Image className="w-5 h-5 text-gray-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">{uploadedFile.name}</h3>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                {!isLoading && (
                  <button
                    onClick={resetUpload}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Upload Different Image
                  </button>
                )}
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex justify-center">
                <img
                  src={previewUrl!}
                  alt="Uploaded template"
                  className="max-w-full max-h-96 rounded-lg shadow-md"
                />
              </div>
            </div>
          </div>

          {/* Analysis Progress */}
          {isLoading && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-4">
                <Loader className="w-6 h-6 text-blue-500 animate-spin" />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">Analyzing Image</h3>
                  <p className="text-gray-600">{analysisProgress}</p>
                </div>
              </div>
              
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300 animate-pulse" style={{ width: '60%' }} />
                </div>
              </div>
            </div>
          )}

          {/* Analysis Complete */}
          {analysisProgress === 'Analysis complete!' && !isLoading && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <div>
                  <h3 className="font-semibold text-green-900">Analysis Complete!</h3>
                  <p className="text-green-700">Your template has been analyzed and is ready for editing.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tips Section */}
      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-blue-500 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Tips for Best Results</h3>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>• Use high-resolution images (at least 800x800 pixels)</li>
              <li>• Ensure text is clearly readable and not too small</li>
              <li>• Choose templates with good contrast between text and background</li>
              <li>• Avoid heavily compressed or blurry images</li>
              <li>• Templates with clear layout structure work best</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;