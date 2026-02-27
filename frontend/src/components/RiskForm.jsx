import React, { useState } from "react";
import { IL_ILCE_DATA } from "../constants/cityData";
import { collatorTR } from "../utils/utils";
import { useGeolocation } from "../hooks/useGeolocation";

const RiskForm = ({ onSubmit, loading: subLoading }) => {
  const [formData, setFormData] = useState({
    il: "",
    ilce: "",
    yapimYili: "",
    katSayisi: "",
    zeminDukkan: "hayir",
    bitisik: "hayir",
    bitisikHiza: "uyumlu",
    kullanimAmaci: "konut",
    kisaKolon: "yok",
    agirCikma: "yok",
    planTipi: "dikdortgen",
    hasar: "yok",
    ultrasonikSesHizi: "",
    geriSicramaSayisi: "",
    corrosion: "-200",
    zeminSinifi: "",
    latitude: null,
    longitude: null,
  });

  const { getPosition, loading: geoLoading, status: geoStatus } = useGeolocation();

  const iller = React.useMemo(() => {
    return [...IL_ILCE_DATA.iller].sort((a, b) =>
      collatorTR.compare(a.ad, b.ad),
    );
  }, []);

  const ilceler = React.useMemo(() => {
    if (formData.il) {
      const ilObj = IL_ILCE_DATA.iller.find((x) => x.slug === formData.il);
      return (ilObj?.ilceler || []).sort((a, b) => collatorTR.compare(a, b));
    }
    return [];
  }, [formData.il]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleLocation = async () => {
    const loc = await getPosition();
    if (loc) {
      setFormData((prev) => ({
        ...prev,
        il: loc.il,
        ilce: loc.ilce,
        latitude: loc.latitude || null,
        longitude: loc.longitude || null,
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Sayısal değerleri dönüştür
    const processedData = {
      ...formData,
      yapimYili: parseInt(formData.yapimYili),
      katSayisi: parseInt(formData.katSayisi),
      ultrasonikSesHizi: parseFloat(formData.ultrasonikSesHizi),
      geriSicramaSayisi: parseFloat(formData.geriSicramaSayisi),
      corrosion: parseFloat(formData.corrosion),
      latitude: formData.latitude,
      longitude: formData.longitude,
      crackPuan: 0, // Varsayılan değer
    };

    onSubmit(processedData);
  };

  return (
    <section className="card">
      <h2>Bina Bilgileri Formu</h2>
      <form onSubmit={handleSubmit}>
        <div
          className="layout"
          style={{
            gridTemplateColumns: "1fr 1fr",
            display: "grid",
            gap: "20px",
          }}
        >
          <div className="field">
            <label>İl</label>
            <select
              name="il"
              value={formData.il}
              onChange={handleChange}
              required
            >
              <option value="" disabled>
                İl seçin
              </option>
              {iller.map((il) => (
                <option key={il.slug} value={il.slug}>
                  {il.ad}
                </option>
              ))}
            </select>
            <small>İl seçiniz veya “Konumu Bul” ile otomatik doldurunuz.</small>
          </div>

          <div className="field">
            <label>İlçe</label>
            <select
              name="ilce"
              value={formData.ilce}
              onChange={handleChange}
              required
              disabled={!formData.il}
            >
              <option value="" disabled>
                İlçe seçin
              </option>
              {ilceler.map((ilce) => (
                <option key={ilce} value={ilce}>
                  {ilce}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="button" onClick={handleLocation} className="location-btn">
          {geoLoading ? "⏳ Konum Alınıyor..." : "📍 Konumumu Bul ve Doldur"}
        </button>
        {geoStatus && (
          <p
            style={{ color: "#fbbf24", fontSize: "0.85rem", marginTop: "5px" }}
          >
            {geoStatus}
          </p>
        )}

        <div
          className="layout"
          style={{
            gridTemplateColumns: "1fr 1fr",
            display: "grid",
            gap: "20px",
            marginTop: "12px",
          }}
        >
          <div className="field">
            <label>Yapım Yılı</label>
            <input
              type="number"
              name="yapimYili"
              value={formData.yapimYili}
              onChange={handleChange}
              min="1800"
              max="2025"
              placeholder="Örn: 1998"
              required
            />
          </div>
          <div className="field">
            <label>Kat Sayısı</label>
            <input
              type="number"
              name="katSayisi"
              value={formData.katSayisi}
              onChange={handleChange}
              min="1"
              max="100"
              placeholder="Örn: 7"
              required
            />
          </div>
        </div>

        <div className="field">
          <label>Zemin Katta Dükkân / Geniş Açıklık Var mı?</label>
          <div className="inline-options">
            {["evet", "hayir"].map((option) => (
              <label key={option}>
                <input
                  type="radio"
                  name="zeminDukkan"
                  value={option}
                  checked={formData.zeminDukkan === option}
                  onChange={handleChange}
                />
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div className="field">
          <label>Bina Bitişik Nizam mı?</label>
          <div className="inline-options">
            {["evet", "hayir"].map((option) => (
              <label key={option}>
                <input
                  type="radio"
                  name="bitisik"
                  value={option}
                  checked={formData.bitisik === option}
                  onChange={handleChange}
                />
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </label>
            ))}
          </div>
        </div>

        {formData.bitisik === "evet" && (
          <div className="field">
            <label>Bitişik Binayla Kat Hizası</label>
            <select
              name="bitisikHiza"
              value={formData.bitisikHiza}
              onChange={handleChange}
            >
              <option value="uyumlu">Uyumlu / Aynı Hiza</option>
              <option value="farkli">Farklı (Çarpışma Riski)</option>
            </select>
          </div>
        )}

        <div className="field">
          <label>Bina Kullanım Amacı</label>
          <select
            name="kullanimAmaci"
            value={formData.kullanimAmaci}
            onChange={handleChange}
          >
            <option value="konut">Konut</option>
            <option value="isyeri">İşyeri / Ofis</option>
            <option value="okul">Okul</option>
            <option value="hastane">Hastane</option>
            <option value="sanayi">Sanayi</option>
            <option value="diger">Diğer</option>
          </select>
        </div>

        <div className="field">
          <label>Kısa Kolon Var mı?</label>
          <div className="inline-options">
            {["yok", "var", "emin_degil"].map((option) => (
              <label key={option}>
                <input
                  type="radio"
                  name="kisaKolon"
                  value={option}
                  checked={formData.kisaKolon === option}
                  onChange={handleChange}
                />
                {option.replace("_", " ").charAt(0).toUpperCase() +
                  option.replace("_", " ").slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div className="field">
          <label>Ağır Çıkma (Balkon/Konsol)</label>
          <select
            name="agirCikma"
            value={formData.agirCikma}
            onChange={handleChange}
          >
            <option value="yok">Yok</option>
            <option value="hafif">Hafif</option>
            <option value="buyuk">Büyük</option>
          </select>
        </div>

        <div className="field">
          <label>Plan Tipi</label>
          <select
            name="planTipi"
            value={formData.planTipi}
            onChange={handleChange}
          >
            <option value="dikdortgen">Dikdörtgen / Düzenli</option>
            <option value="L">L Tipi</option>
            <option value="T">T Tipi</option>
            <option value="U">U Tipi</option>
            <option value="kompleks">Kompleks / Düzensiz</option>
          </select>
        </div>

        <div className="field">
          <label>Gözle Görülür Hasar Durumu</label>
          <select name="hasar" value={formData.hasar} onChange={handleChange}>
            <option value="yok">Yok</option>
            <option value="hafif">Hafif (Sıva çatlağı vb.)</option>
            <option value="kolon">Ciddi (Kolon/Kiriş Hasarı)</option>
          </select>
        </div>

        <hr
          style={{
            border: 0,
            borderTop: "1px solid #334155",
            margin: "20px 0",
          }}
        />

        <div className="field">
          <label>Ultrasonik Ses Hızı (UPV) - km/s</label>
          <input
            type="number"
            name="ultrasonikSesHizi"
            value={formData.ultrasonikSesHizi}
            onChange={handleChange}
            step="0.01"
            min="0.1"
            placeholder="Örn: 4.5"
            required
          />
        </div>

        <div className="field">
          <label>Schmidt Çekici (RN)</label>
          <input
            type="number"
            name="geriSicramaSayisi"
            value={formData.geriSicramaSayisi}
            onChange={handleChange}
            min="1"
            placeholder="Örn: 30"
            required
          />
        </div>

        <div className="field">
          <label>Korozyon Potansiyeli (mV)</label>
          <input
            type="number"
            name="corrosion"
            value={formData.corrosion}
            onChange={handleChange}
            required
          />
          <small>Negatif değerler risk gösterir.</small>
        </div>

        <div className="field">
          <label>Zemin Sınıfı</label>
          <select
            name="zeminSinifi"
            value={formData.zeminSinifi}
            onChange={handleChange}
          >
            <option value="">Otomatik Tahmin Et (Haritadan)</option>
            <option value="Z1">Z1 (Çok Sağlam Kaya)</option>
            <option value="Z2">Z2 (Sağlam Zemin)</option>
            <option value="Z3">Z3 (Orta Zemin)</option>
            <option value="Z4">Z4 (Zayıf / Alüvyon)</option>
          </select>
        </div>

        <button type="submit" disabled={subLoading}>
          {subLoading ? (
            <>
              <span
                className="loader"
                style={{
                  width: "15px",
                  height: "15px",
                  borderTopColor: "#fff",
                  borderLeftColor: "#fff",
                }}
              ></span>
              Hesaplanıyor...
            </>
          ) : (
            "Risk Skorunu Hesapla"
          )}
        </button>
      </form>
    </section>
  );
};

export default RiskForm;
