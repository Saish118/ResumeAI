import React, { useRef, useState } from 'react';
import { UploadCloud, File, X, AlertCircle, History } from 'lucide-react';

const MAX_FILE_SIZE_MB = 10;

export default function ResumeUploader({
  selectedFile,
  onFileSelect,
  onFileRemove,
  errorMessage,
  setErrorMessage,
  isRestored = false,
  restoredFilename = '',
  onClearRestored = null
}) {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const validateAndPassFile = (file) => {
    setErrorMessage('');
    if (!file) return;

    const extension = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(extension)) {
      setErrorMessage('Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx).');
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > MAX_FILE_SIZE_MB) {
      setErrorMessage(`File size exceeds maximum limit of ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }

    onFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndPassFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndPassFile(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="uploader-card" id="upload">
      {isRestored && restoredFilename && !selectedFile && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          color: '#1e40af',
          padding: '10px 14px',
          borderRadius: 'var(--radius-sm, 6px)',
          marginBottom: '14px',
          fontSize: '0.875rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={16} />
            <span>Previous analysis restored: <strong>{restoredFilename}</strong></span>
          </div>
          {onClearRestored && (
            <button
              type="button"
              onClick={onClearRestored}
              style={{
                background: 'none',
                border: 'none',
                color: '#1d4ed8',
                cursor: 'pointer',
                fontSize: '0.8125rem',
                fontWeight: '600',
                textDecoration: 'underline'
              }}
            >
              Clear / Reset
            </button>
          )}
        </div>
      )}

      {errorMessage && (
        <div className="error-alert" role="alert">
          <AlertCircle size={18} />
          <span>{errorMessage}</span>
        </div>
      )}

      {!selectedFile ? (
        <div
          className={`uploader-dropzone ${isDragActive ? 'drag-active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="dropzone-icon">
            <UploadCloud size={24} />
          </div>
          <h3 className="dropzone-title">Upload your resume here</h3>
          <p className="dropzone-subtext">Drag and drop your document file, or click to browse</p>

          <button type="button" className="btn-file-select" onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current?.click();
          }}>
            Choose File
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="hidden-file-input"
            onChange={handleFileChange}
          />

          <div className="file-format-hints">
            Supported formats: PDF (.pdf), Word (.docx) — Max {MAX_FILE_SIZE_MB}MB
          </div>
        </div>
      ) : (
        <div className="selected-file-box">
          <div className="file-info">
            <File className="file-icon" />
            <div>
              <div className="file-name">{selectedFile.name}</div>
              <div className="file-meta">{formatFileSize(selectedFile.size)} • Ready for analysis</div>
            </div>
          </div>
          <button type="button" className="btn-remove-file" onClick={onFileRemove}>
            <X size={16} />
            <span>Remove</span>
          </button>
        </div>
      )}
    </div>
  );
}
