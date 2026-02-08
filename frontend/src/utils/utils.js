export function normalizeTR(text) {
    if (!text) return "";
    return text.toString().trim()
        .replaceAll("ğ", "g").replaceAll("Ğ", "g")
        .replaceAll("ı", "i").replaceAll("İ", "i").replaceAll("I", "i")
        .replaceAll("ö", "o").replaceAll("Ö", "o")
        .replaceAll("ş", "s").replaceAll("Ş", "s")
        .replaceAll("ü", "u").replaceAll("Ü", "u")
        .replaceAll("ç", "c").replaceAll("Ç", "c")
        .toLowerCase()
        .normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[\s-]+/g, "");
}

export const collatorTR = new Intl.Collator("tr-TR", { sensitivity: "base" });
