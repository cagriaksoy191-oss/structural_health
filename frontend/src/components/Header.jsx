import React from 'react';

const Header = () => {
    return (
        <header className="mb-6 border-b border-gray-800 pb-4">
            <h1 className="text-2xl font-bold text-gray-100 mb-2">Yapı Sağlığı – Web Tabanlı Ön Tarama Aracı</h1>
            <p className="text-sm text-gray-400">V12 Titanium Backend Entegrasyonu (Qwen3 & Fuzzy Logic)</p>
            <p className="text-xs text-gray-500 mt-1 italic">
                Bu sistem, sadece bilgilendirme amaçlıdır ve resmi deprem performans analizi yerine geçmez.
            </p>
        </header>
    );
};

export default Header;
