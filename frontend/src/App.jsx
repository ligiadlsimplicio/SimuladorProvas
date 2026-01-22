import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) {
      alert("Por favor, selecione um arquivo PDF primeiro!")
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Envia para o nosso Backend em Python
      const response = await fetch('http://127.0.0.1:8000/upload/', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResultado(data)
    } catch (error) {
      console.error("Erro:", error)
      alert("Erro ao conectar com o servidor.")
    }
    setLoading(false)
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>📑 Leitor de Editais PWA</h1>
      
      <div style={{ border: '2px dashed #ccc', padding: '20px', borderRadius: '10px' }}>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button 
          onClick={handleUpload} 
          disabled={loading}
          style={{ marginLeft: '10px', padding: '10px 20px', cursor: 'pointer' }}
        >
          {loading ? "Processando..." : "Analisar Edital"}
        </button>
      </div>

      {resultado && (
        <div style={{ marginTop: '20px', textAlign: 'left' }}>
          <h2>Resultado:</h2>
          <p><strong>Arquivo:</strong> {resultado.filename}</p>
          <p><strong>Páginas:</strong> {resultado.total_paginas}</p>
          <div style={{ background: '#f4f4f4', padding: '10px', borderRadius: '5px' }}>
            <strong>Prévia do Texto:</strong>
            <p>{resultado.preview_texto}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App