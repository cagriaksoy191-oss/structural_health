import { useState } from 'react';
import { normalizeTR } from '../utils/utils';
import { IL_ILCE_DATA } from '../constants/cityData';

export const useGeolocation = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('');

    const getPosition = async () => {
        if (!navigator.geolocation) {
            setError("Tarayıcınız konum özelliğini desteklemiyor.");
            return null;
        }

        setLoading(true);
        setError(null);
        setStatus("📍 Konum izni bekleniyor...");

        const options = {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 600000
        };

        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, options);
            });

            const { latitude: lat, longitude: lon } = position.coords;
            setStatus("🔍 Konum bulundu, adres aranıyor...");

            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&accept-language=tr`, {
                headers: { 'User-Agent': 'YapiSagligi-App/1.0' }
            });

            if (!res.ok) throw new Error("Adres servisi yanıt vermedi");

            const data = await res.json();
            const addr = data.address || {};
            const ilText = addr.province || addr.state || addr.city || "";
            const ilceText = addr.county || addr.district || addr.town || "";

            if (!ilText) {
                throw new Error("İl tespit edilemedi.");
            }

            const ilSlug = normalizeTR(ilText);
            const ilObj = IL_ILCE_DATA.iller.find(x => x.slug === ilSlug);

            if (!ilObj) {
                throw new Error(`"${ilText}" ili listede bulunamadı.`);
            }

            const targetIlce = normalizeTR(ilceText);
            const match = ilObj.ilceler.find(x => normalizeTR(x) === targetIlce);

            setStatus(`✅ Konum bulundu: ${ilObj.ad}${match ? " / " + match : ""}`);
            setLoading(false);

            return {
                il: ilObj.slug,
                ilce: match || ""
            };

        } catch (err) {
            console.error("Geoloc error:", err);
            let msg = "Konum tespit edilemedi.";
            if (err.code === 1) msg = "Konum izni verilmedi.";
            else if (err.code === 2) msg = "Konum alınamadı.";
            else if (err.code === 3) msg = "Zaman aşımı.";

            setError(msg);
            setStatus("⚠️ " + msg);
            setLoading(false);
            return null;
        }
    };

    return { getPosition, loading, error, status };
};
