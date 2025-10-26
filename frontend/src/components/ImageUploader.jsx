import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

export default function ImageUploader({ onFileChange, initialImage = null }) {
  const [preview, setPreview] = useState(initialImage)

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0]
    if (file) {
      onFileChange(file)
      setPreview(URL.createObjectURL(file))
    }
  }, [onFileChange])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.png', '.jpg', '.gif', '.webp'] },
    multiple: false,
  })

  const removeImage = (e) => {
    e.stopPropagation(); // Evita que se abra el selector de archivos
    setPreview(null);
    onFileChange(null);
  }

  return (
    <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
      <input {...getInputProps()} />
      {preview ? (
        <>
          <img src={preview} alt="Previsualización" className="preview-img" />
          <button type="button" className="remove-btn" onClick={removeImage}>&times;</button>
        </>
      ) : (
        <p>{isDragActive ? 'Suelta la imagen aquí...' : 'Arrastra una imagen o haz clic para seleccionar'}</p>
      )}
      <style>{`
        .dropzone {
          border: 2px dashed #ccc; border-radius: 8px; padding: 20px; text-align: center;
          cursor: pointer; transition: border .24s ease-in-out; position: relative; min-height: 120px;
          display: grid; place-items: center;
        }
        .dropzone.active { border-color: var(--primary); }
        .preview-img { max-width: 100%; max-height: 150px; object-fit: contain; }
        .remove-btn {
          position: absolute; top: 5px; right: 5px; background: #0008; color: white;
          border: none; border-radius: 50%; width: 24px; height: 24px;
          cursor: pointer; font-size: 16px; line-height: 24px;
        }
      `}</style>
    </div>
  )
}