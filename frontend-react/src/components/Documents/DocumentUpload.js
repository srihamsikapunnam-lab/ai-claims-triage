import React, { useState, useRef } from 'react';
import apiClient from '../../utils/apiClient';
import './DocumentUpload.css';

const DocumentUpload = ({ claimId, onUploadComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentType, setDocumentType] = useState('medical_report');
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const documentTypes = [
    { value: 'medical_report', label: 'Medical Report' },
    { value: 'bill', label: 'Medical Bill' },
    { value: 'prescription', label: 'Prescription' },
    { value: 'id_proof', label: 'ID Proof' },
    { value: 'insurance_card', label: 'Insurance Card' },
    { value: 'other', label: 'Other' },
  ];

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError('');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', documentType);
      if (description) {
        formData.append('description', description);
      }

      await apiClient.uploadFile(`/claims/${claimId}/documents`, formData);
      
      setSuccess('Document uploaded successfully!');
      setSelectedFile(null);
      setDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <h3>📎 Upload Documents</h3>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div
        className="drop-zone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
          style={{ display: 'none' }}
        />
        {selectedFile ? (
          <div className="file-selected">
            <span>📄 {selectedFile.name}</span>
            <span className="file-size">
              ({(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
          </div>
        ) : (
          <div className="drop-zone-content">
            <p>📁 Click or drag file here to upload</p>
            <p className="drop-zone-hint">
              Supported: PDF, PNG, JPG, DOC (Max 10MB)
            </p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Document Type</label>
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
        >
          {documentTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Description (Optional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows="2"
          placeholder="Add any notes about this document..."
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={!selectedFile || isUploading}
        className="upload-button"
      >
        {isUploading ? 'Uploading...' : '⬆️ Upload Document'}
      </button>
    </div>
  );
};

export default DocumentUpload;
