"""
Transaction Classifier - Pure Python Logic
Bisa dipakai standalone, tidak tergantung FastAPI/DB
"""

import re
from typing import Optional, Tuple, Dict

class TransactionClassifier:
    """Rule-based classifier for Indonesian transaction text"""
    
    def __init__(self):
        # PEMASUKAN patterns
        self.pemasukan_patterns = {
            'gaji': ['gaji', 'gajian', 'salary', 'upah'],
            'bonus': ['bonus', 'tunjangan', 'thr', 'uang lembur'],
            'hadiah': ['hadiah', 'kado', 'gift', 'angpao'],
            'cashback': ['cashback', 'cash back', 'refund', 'reimburse'],
            'transfer': ['transfer', 'kirim', 'dari']
        }
        
        # PENGELUARAN patterns
        self.pengeluaran_patterns = {
            'makan': ['makan', 'warteg', 'resto', 'rumah makan', 'lunch', 'dinner', 'sarapan'],
            'jajan': ['jajan', 'nge', 'ngemil', 'camilan', 'snack', 'jajanan'],
            'transportasi': ['grab', 'gojek', 'ojek', 'taksi', 'transjakarta', 'angkot', 'bajaj', 'bensin'],
            'tagihan': ['listrik', 'pln', 'token', 'air', 'pdam', 'pam', 'internet'],
            'pulsa': ['pulsa', 'kuota', 'data', 'paket data'],
            'hiburan': ['nonton', 'bioskop', 'film', 'spotify', 'netflix', 'youtube', 'game'],
            'kesehatan': ['obat', 'apotek', 'dokter', 'rumah sakit', 'klinik', 'medical'],
            'belanja': ['beli', 'belanja', 'shop', 'order', 'beliin', 'belikan']
        }
    
    def extract_harga(self, text: str) -> Tuple[Optional[int], str]:
        """Extract harga dari text dengan berbagai format"""
        patterns = [
            (r'(\d{1,3}(?:\.\d{3})*)\s*(rb|ribu)', 1000),
            (r'(\d{1,3}(?:\.\d{3})*)\s*(jt|juta)', 1_000_000),
            (r'(\d{1,3}(?:\.\d{3})*)k', 1000),
            (r'rp\.?\s*(\d{1,3}(?:\.\d{3})*)', 1),
            (r'\b(\d{4,})\b', 1)
        ]
        
        text_lower = text.lower()
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text_lower)
            if match:
                num_str = None
                for i in range(1, len(match.groups()) + 1):
                    if match.group(i) and match.group(i).strip():
                        num_str = match.group(i)
                        break
                
                if num_str:
                    try:
                        num_clean = num_str.replace('.', '').replace(',', '.')
                        harga = int(float(num_clean)) * multiplier
                        text_clean = re.sub(pattern, '', text_lower, flags=re.IGNORECASE).strip()
                        return harga, text_clean
                    except:
                        continue
        
        return None, text_lower
    
    def detect_kategori(self, text: str, harga: Optional[int]) -> Tuple[str, str, str]:
        """Detect kategori utama, detail, dan confidence"""
        text_lower = text.lower()
        
        # PEMASUKAN - High confidence
        for detail, keywords in self.pemasukan_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Special case: "transfer ke" = pengeluaran
                    if detail == 'transfer':
                        if 'ke' in text_lower and 'dari' not in text_lower:
                            continue
                    
                    return "Pemasukan", detail, "high"
        
        # PENGELUARAN - High confidence
        for detail, keywords in self.pengeluaran_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return "Pengeluaran", detail, "high"
        
        # PEMASUKAN - Medium confidence
        if any(word in text_lower for word in ['dapat', 'terima', 'masuk']) and harga and harga > 500_000:
            return "Pemasukan", "pemasukan", "medium"
        
        # Default - Low confidence
        if harga and harga > 0:
            return "Pengeluaran", "lainnya", "low"
        
        return "Pemasukan", "lainnya", "low"
    
    def extract_item(self, text: str) -> str:
        """Extract item dari text"""
        item = re.sub(r'[^\w\s]', ' ', text)
        item = re.sub(r'\s+', ' ', item).strip()
        item = re.sub(r'\b\d+\b', '', item)
        item = re.sub(r'\s+', ' ', item).strip()
        
        stopwords = ['untuk', 'dengan', 'ke', 'di', 'pada', 'dan', 'atau', 'yang', 
                    'ini', 'itu', 'saya', 'aku', 'kami', 'kita', 'mereka', 'dia',
                    'buat', 'lagi', 'sudah', 'akan', 'mau', 'ingin']
        
        words = item.lower().split()
        filtered = [w for w in words if w not in stopwords and len(w) > 1]
        item_clean = ' '.join(filtered).title()
        
        return item_clean if item_clean else "Tidak diketahui"
    
    def classify(self, text: str) -> Dict[str, any]:
        """Main classification method"""
        harga, text_no_price = self.extract_harga(text)
        kategori_utama, kategori_detail, confidence = self.detect_kategori(text, harga)
        item = self.extract_item(text_no_price)
        
        return {
            "kategori_utama": kategori_utama,
            "kategori_detail": kategori_detail,
            "item": item,
            "harga": harga,
            "confidence": confidence
        }


# Singleton instance
classifier = TransactionClassifier()