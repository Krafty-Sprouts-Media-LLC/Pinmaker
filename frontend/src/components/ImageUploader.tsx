import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { API_ENDPOINTS, API_CONFIG } from '../config/api';

interface ImageUploaderProps {
  onImageUpload: (imageUrl: string) => void;
  onAnalysisComplete: (analysis: any) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageUpload, onAnalysisComplete }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      // Create preview URL for immediate display
      const previewUrl = URL.createObjectURL(file);
      onImageUpload(previewUrl);

      // Upload to backend
      const formData = new FormData();
      formData.append('file', file);

      setIsAnalyzing(true);
      const response = await axios.post(API_ENDPOINTS.ANALYZE, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: API_CONFIG.TIMEOUT,
      });

      onAnalysisComplete(response.data);
    } catch (err: any) {
      let errorMessage = 'Failed to upload and analyze image';
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Image analysis is taking longer than expected. Please try with a smaller image or try again later.';
      } else if (err.response?.status === 504) {
        errorMessage = 'Server timeout - the image analysis is taking too long. Please try with a smaller image.';
      } else if (err.response?.status === 413) {
        errorMessage = 'Image file is too large. Please use an image smaller than 10MB.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Server error occurred. Please try again in a few moments.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
      setIsAnalyzing(false);
    }
  }, [onImageUpload, onAnalysisComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: false,
    maxSize: API_CONFIG.MAX_FILE_SIZE
  });

  return (
    <div className="image-uploader">
      <div 
        {...getRootProps()} 
        className={`dropzone ${
          isDragActive ? 'active' : ''
        } ${isUploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <div className="upload-status">
            <div className="spinner"></div>
            <p>{isAnalyzing ? 'Analyzing image...' : 'Uploading...'}</p>
          </div>
        ) : (
          <div className="upload-prompt">
            {isDragActive ? (
              <p>Drop the image here...</p>
            ) : (
              <>
                <div className="upload-icon">📷</div>
                <p>Drag & drop an image here, or click to select</p>
                <p className="upload-hint">Supports: JPEG, PNG, GIF, WebP (max 10MB)</p>
              </>
            )}
          </div>
        )}
      </div>
      
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;