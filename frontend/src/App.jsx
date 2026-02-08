import { useState } from 'react'
import RiskForm from './components/RiskForm'

const API_URL = "http://127.0.0.1:8000/api/risk-hesapla";

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCalculate = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error("Sunucu hatası: " + response.statusText);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Bağlantı hatası: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Yapı Sağlığı – Web Tabanlı Ön Tarama Aracı</h1>
        <p>V12 Titanium Backend Entegrasyonu (Qwen3 & Fuzzy Logic)</p>
        <p className="muted">Bu sistem, sadece bilgilendirme amaçlıdır ve resmi deprem performans analizi yerine geçmez.</p>
      </header>

      <div className="layout">
        <RiskForm onSubmit={handleCalculate} loading={loading} />

        <section className="card">
          <div className="result-header">
            <h2>Analiz Sonucu</h2>
            {result && (
              <span className={`badge ${result.genelSeviye === "Yüksek" ? "badge-high" : (result.genelSeviye === "Orta" ? "badge-mid" : "badge-low")}`}>
                {result.genelSeviye} Risk
              </span>
            )}
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
              <div className="loader" style={{ width: '40px', height: '40px' }}></div>
              <p style={{ marginTop: '15px' }}>Yapay Zeka (Qwen3) verileri analiz ediyor...<br /><small>Bu işlem 5-10 saniye sürebilir.</small></p>
            </div>
          )}

          {error && (
            <div className="warning" style={{ borderColor: '#ef4444', color: '#ef4444', background: 'rgba(239, 68, 68, 0.1)' }}>
              <strong>Hata:</strong> {error}
            </div>
          )}

          {!result && !loading && !error && (
            <p className="muted" style={{ textAlign: 'center', padding: '20px' }}>
              Formu doldurup hesapla butonuna bastığınızda sonuçlar burada görünecektir.
            </p>
          )}

          {result && !loading && (
            <div id="resultContent">
              <div className="score-box">
                <div className="score-val">{result.healthScore}</div>
                <div className="score-label">Sağlık Skoru (100 Üzerinden)</div>
              </div>

              <div className="pill-row">
                <span className="pill" style={{ borderColor: '#3b82f6', color: '#93c5fd' }}><strong>Deprem Riski:</strong> {result.depremSeviye.toUpperCase()}</span>
                <span className="pill" style={{ borderColor: '#f59e0b', color: '#fcd34d' }}><strong>Yapı Puanı:</strong> {result.toplamYapisalRisk}</span>
                <span className="pill"><strong>Beton:</strong> {result.basincDayanimi ? result.basincDayanimi.toFixed(1) + " MPa" : "Veri Yok"}</span>
                <span className="pill"><strong>Korozyon:</strong> {result.corrosion} mV</span>
                <span className="pill"><strong>Zemin:</strong> {result.zeminSinifi || "Tahmin"}</span>
              </div>

              <div className="pill-row">
                {result.detaylar.map((d, i) => <span key={i} className="pill">{d}</span>)}
              </div>

              <div className="ai-box">
                <div className="ai-title">🤖 Yapay Zeka Değerlendirmesi</div>
                {result.aciklama}
              </div>

              <div className="warning">
                <strong>⚠️ Yasal Uyarı:</strong> Bu rapor bir ön bilgilendirmedir. Resmi belge niteliği taşımaz. Kesin sonuç için lisanslı kuruluşlara başvurunuz.
              </div>
            </div>
          )}
        </section>
      </div>

    </div>
  )
}

export default App
