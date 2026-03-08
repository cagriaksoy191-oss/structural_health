import React from 'react';

const ResultCard = ({ result, loading }) => {
    if (loading) {
        return (
            <section className="bg-card rounded-2xl p-6 border border-border flex flex-col items-center justify-center min-h-[400px]">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-gray-400 text-center animate-pulse">
                    Yapay Zeka (Qwen3) verileri analiz ediyor...<br />
                    <span className="text-xs text-gray-500">Bu işlem 5-10 saniye sürebilir.</span>
                </p>
            </section>
        );
    }

    if (!result) {
        return (
            <section className="bg-card rounded-2xl p-6 border border-border flex items-center justify-center min-h-[400px]">
                <p className="text-gray-500 text-center max-w-xs">
                    Formu doldurup hesapla butonuna bastığınızda sonuçlar burada görünecektir.
                </p>
            </section>
        );
    }

    const {
        genelSeviye,
        healthScore,
        depremSeviye,
        toplamYapisalRisk,
        basincDayanimi,
        corrosion,
        zeminSinifi,
        detaylar,
        aciklama,
        bks,
        binaYukseklik,
        dts,
        earthquakeClasses,
        pdfDownloadUrl
    } = result;

    const badgeColors = {
        'Yüksek': 'bg-red-900/30 text-red-300 border-red-500',
        'Orta': 'bg-amber-900/30 text-amber-300 border-amber-500',
        'Düşük': 'bg-green-900/30 text-green-300 border-green-500'
    };

    return (
        <section className="bg-card rounded-2xl p-6 border border-border shadow-2xl animate-in fade-in zoom-in duration-500">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-100">Analiz Sonucu</h2>
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${badgeColors[genelSeviye] || 'bg-gray-800 text-gray-300'}`}>
                    {genelSeviye} RİSK
                </span>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center mb-6">
                <div className="text-5xl font-extrabold text-blue-400 mb-2 leading-none">{healthScore}</div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Sağlık Skoru (100 Üzerinden)</div>
            </div>

            <div className="flex flex-wrap gap-2 mb-6">
                <StatPill label="Deprem Riski" value={depremSeviye?.toUpperCase()} color="border-blue-500 text-blue-300" />
                <StatPill label="Yapı Puanı" value={toplamYapisalRisk} color="border-amber-500 text-amber-300" />
                <StatPill label="Beton" value={basincDayanimi ? `${basincDayanimi.toFixed(1)} MPa` : 'N/A'} />
                <StatPill label="Korozyon" value={`${corrosion} mV`} />
                <StatPill label="Zemin" value={zeminSinifi || 'Tahmin'} />
                <StatPill label="BKS" value={bks || '-'} />
                <StatPill label="BYS" value={binaYukseklik ? `${binaYukseklik}m` : '-'} />
                <StatPill label="DTS" value={dts || '-'} />
            </div>

            <div className="flex flex-wrap gap-2 mb-8">
                {detaylar?.map((detail, idx) => (
                    <span key={idx} className="bg-slate-800 border border-slate-700 text-slate-300 text-[11px] px-2 py-1 rounded">
                        {detail}
                    </span>
                ))}
            </div>

            <div className="bg-slate-800/50 border-l-4 border-purple-500 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2 text-purple-400 font-bold text-sm mb-2">
                    <span>🤖</span> Yapay Zeka Değerlendirmesi
                </div>
                <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap italic">
                    {aciklama}
                </p>
            </div>

            {earthquakeClasses && Object.keys(earthquakeClasses).length > 0 && (
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-6">
                    <div className="text-sm font-bold text-slate-300 mb-2">📡 AFAD Son 50 Yıl Deprem Verisi (Bölge)</div>
                    <div className="flex flex-wrap gap-4">
                        {Object.entries(earthquakeClasses).map(([cls, count]) => (
                            <div key={cls} className="text-xs text-slate-400 bg-slate-900 border border-slate-600 px-3 py-1 rounded">
                                <span className="font-bold text-slate-200">{cls}:</span> {count} Adet
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {pdfDownloadUrl && (
                <div className="flex justify-center mb-6">
                    <a href={`http://127.0.0.1:8000${pdfDownloadUrl}`} target="_blank" rel="noreferrer"
                        className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-xl transition-all flex items-center gap-2 shadow-lg hover:shadow-purple-500/50">
                        📄 Yapay Zeka Analiz Raporunu İndir (PDF)
                    </a>
                </div>
            )}

            <div className="bg-amber-500/10 border border-dashed border-amber-500/50 rounded-lg p-3 text-center">
                <p className="text-[10px] text-amber-200 leading-tight">
                    <strong>⚠️ Yasal Uyarı:</strong> Bu rapor bir ön bilgilendirmedir. Resmi belge niteliği taşımaz. Kesin sonuç için lisanslı kuruluşlara başvurunuz.
                </p>
            </div>
        </section>
    );
};

const StatPill = ({ label, value, color = "border-slate-700 text-slate-300" }) => (
    <span className={`border ${color} bg-slate-900/50 text-[11px] px-3 py-1 rounded-lg flex items-center gap-2`}>
        <span className="opacity-60">{label}:</span>
        <span className="font-bold">{value}</span>
    </span>
);

export default ResultCard;
