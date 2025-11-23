# City Configurations for Data Collection
# Format: 'key': {'name': 'City Name', 'country': 'Country Name', 'bbox': {...}}

CITIES = {
    # --- THAILAND ---
    'bangkok': {
        'name': 'Bangkok',
        'country': 'Thailand',
        'bbox': {'north': 13.95, 'south': 13.50, 'east': 100.90, 'west': 100.30}
    },
    'chiang_mai': {
        'name': 'Chiang Mai',
        'country': 'Thailand',
        'bbox': {'north': 18.85, 'south': 18.70, 'east': 99.05, 'west': 98.90}
    },
    'phuket': {
        'name': 'Phuket',
        'country': 'Thailand',
        'bbox': {'north': 8.20, 'south': 7.75, 'east': 98.45, 'west': 98.25}
    },
    'pattaya': {
        'name': 'Pattaya',
        'country': 'Thailand',
        'bbox': {'north': 13.00, 'south': 12.85, 'east': 100.95, 'west': 100.85}
    },
    'krabi': {
        'name': 'Krabi',
        'country': 'Thailand',
        'bbox': {'north': 8.15, 'south': 7.95, 'east': 98.95, 'west': 98.85}
    },
    'ayutthaya': {
        'name': 'Ayutthaya',
        'country': 'Thailand',
        'bbox': {'north': 14.40, 'south': 14.30, 'east': 100.60, 'west': 100.50}
    },
    'koh_samui': {
        'name': 'Koh Samui',
        'country': 'Thailand',
        'bbox': {'north': 9.60, 'south': 9.45, 'east': 100.10, 'west': 99.95}
    },
    'hua_hin': {
        'name': 'Hua Hin',
        'country': 'Thailand',
        'bbox': {'north': 12.65, 'south': 12.50, 'east': 99.98, 'west': 99.90}
    },
    'chiang_rai': { 'name': 'Chiang Rai', 'country': 'Thailand', 'bbox': {'north': 20.00, 'south': 19.85, 'east': 99.90, 'west': 99.75} },
    'pai': { 'name': 'Pai', 'country': 'Thailand', 'bbox': {'north': 19.40, 'south': 19.30, 'east': 98.50, 'west': 98.40} },
    'kanchanaburi': { 'name': 'Kanchanaburi', 'country': 'Thailand', 'bbox': {'north': 14.10, 'south': 13.90, 'east': 99.60, 'west': 99.40} },
    'sukhothai': { 'name': 'Sukhothai', 'country': 'Thailand', 'bbox': {'north': 17.05, 'south': 16.95, 'east': 99.85, 'west': 99.75} },
    'khao_sok': { 'name': 'Khao Sok', 'country': 'Thailand', 'bbox': {'north': 9.00, 'south': 8.80, 'east': 98.70, 'west': 98.50} },
    'koh_tao': { 'name': 'Koh Tao', 'country': 'Thailand', 'bbox': {'north': 10.15, 'south': 10.05, 'east': 99.85, 'west': 99.80} },
    'koh_phangan': { 'name': 'Koh Phangan', 'country': 'Thailand', 'bbox': {'north': 9.80, 'south': 9.65, 'east': 100.10, 'west': 99.95} },
    'koh_lanta': { 'name': 'Koh Lanta', 'country': 'Thailand', 'bbox': {'north': 7.70, 'south': 7.50, 'east': 99.15, 'west': 99.00} },
    'koh_chang': { 'name': 'Koh Chang', 'country': 'Thailand', 'bbox': {'north': 12.15, 'south': 11.95, 'east': 102.45, 'west': 102.25} },

    # --- VIETNAM ---
    'hanoi': { 'name': 'Hanoi', 'country': 'Vietnam', 'bbox': None },
    'ho_chi_minh_city': {
        'name': 'Ho Chi Minh City',
        'country': 'Vietnam',
        'bbox': {'north': 11.16, 'south': 10.35, 'east': 107.02, 'west': 106.33}
    },
    'da_nang': { 'name': 'Da Nang', 'country': 'Vietnam', 'bbox': {'north': 16.0678, 'south': 16.0471, 'east': 108.2333, 'west': 108.2062} },
    'hoi_an': { 'name': 'Hoi An', 'country': 'Vietnam', 'bbox': {'north': 15.93, 'south': 15.83, 'east': 108.38, 'west': 108.28} },
    'nha_trang': { 'name': 'Nha Trang', 'country': 'Vietnam', 'bbox': {'north': 12.2451, 'south': 12.1450, 'east': 109.1943, 'west': 109.1130} },
    'ha_long': { 'name': 'Ha Long', 'country': 'Vietnam', 'bbox': {'north': 21.01, 'south': 20.91, 'east': 107.09, 'west': 106.99} },
    'sapa': { 'name': 'Sapa', 'country': 'Vietnam', 'bbox': {'north': 22.3565, 'south': 22.3364, 'east': 103.8738, 'west': 103.8438} },
    'hue': { 'name': 'Hue', 'country': 'Vietnam', 'bbox': {'north': 16.4667, 'south': 16.4498, 'east': 107.6000, 'west': 107.5623} },
    'ninh_binh': { 'name': 'Ninh Binh', 'country': 'Vietnam', 'bbox': {'north': 20.28, 'south': 20.23, 'east': 106.00, 'west': 105.95} },
    'da_lat': { 'name': 'Da Lat', 'country': 'Vietnam', 'bbox': {'north': 11.96, 'south': 11.92, 'east': 108.46, 'west': 108.42} },
    'phu_quoc': { 'name': 'Phu Quoc', 'country': 'Vietnam', 'bbox': {'north': 10.4500, 'south': 10.0333, 'east': 104.0667, 'west': 103.8167} },
    'phong_nha': { 'name': 'Phong Nha', 'country': 'Vietnam', 'bbox': {'north': 17.65, 'south': 17.35, 'east': 106.40, 'west': 105.95} },
    'ha_giang': { 'name': 'Ha Giang', 'country': 'Vietnam', 'bbox': {'north': 22.85, 'south': 22.80, 'east': 105.00, 'west': 104.96} },

    # --- INDIA ---
    'delhi': {
        'name': 'Delhi',
        'country': 'India',
        'bbox': {'north': 28.88, 'south': 28.40, 'east': 77.35, 'west': 76.84}
    },
    'mumbai': { 'name': 'Mumbai', 'country': 'India', 'bbox': {'north': 19.27, 'south': 18.89, 'east': 73.00, 'west': 72.77} },
    'jaipur': { 'name': 'Jaipur', 'country': 'India', 'bbox': {'north': 27.00, 'south': 26.75, 'east': 75.90, 'west': 75.70} },
    'agra': { 'name': 'Agra', 'country': 'India', 'bbox': {'north': 27.25, 'south': 27.10, 'east': 78.10, 'west': 77.90} },
    'goa': { 'name': 'Goa', 'country': 'India', 'bbox': {'north': 15.80, 'south': 14.90, 'east': 74.30, 'west': 73.60} },
    'varanasi': { 'name': 'Varanasi', 'country': 'India', 'bbox': {'north': 25.38, 'south': 25.25, 'east': 83.05, 'west': 82.90} },
    'udaipur': { 'name': 'Udaipur', 'country': 'India', 'bbox': {'north': 24.65, 'south': 24.50, 'east': 73.80, 'west': 73.60} },
    'jodhpur': { 'name': 'Jodhpur', 'country': 'India', 'bbox': {'north': 26.40, 'south': 26.20, 'east': 73.15, 'west': 72.90} },
    'jaisalmer': { 'name': 'Jaisalmer', 'country': 'India', 'bbox': {'north': 26.95, 'south': 26.85, 'east': 71.00, 'west': 70.85} },
    'rishikesh': { 'name': 'Rishikesh', 'country': 'India', 'bbox': {'north': 30.15, 'south': 30.05, 'east': 78.35, 'west': 78.25} },
    'kochi': { 'name': 'Kochi', 'country': 'India', 'bbox': {'north': 10.05, 'south': 9.85, 'east': 76.35, 'west': 76.20} },
    'hampi': { 'name': 'Hampi', 'country': 'India', 'bbox': {'north': 15.40, 'south': 15.30, 'east': 76.55, 'west': 76.40} },
    'leh': { 'name': 'Leh', 'country': 'India', 'bbox': {'north': 34.20, 'south': 34.10, 'east': 77.65, 'west': 77.50} },
    'manali': { 'name': 'Manali', 'country': 'India', 'bbox': {'north': 32.30, 'south': 32.20, 'east': 77.25, 'west': 77.15} },
    'darjeeling': { 'name': 'Darjeeling', 'country': 'India', 'bbox': {'north': 27.10, 'south': 27.00, 'east': 88.30, 'west': 88.20} },
    'mysore': { 'name': 'Mysore', 'country': 'India', 'bbox': {'north': 12.35, 'south': 12.25, 'east': 76.70, 'west': 76.60} },
    'amritsar': { 'name': 'Amritsar', 'country': 'India', 'bbox': {'north': 31.70, 'south': 31.55, 'east': 74.95, 'west': 74.80} },
    'pondicherry': { 'name': 'Pondicherry', 'country': 'India', 'bbox': {'north': 12.00, 'south': 11.90, 'east': 79.90, 'west': 79.80} },

    # --- AZERBAIJAN ---
    'baku': {
        'name': 'Baku',
        'country': 'Azerbaijan',
        'bbox': {'north': 40.45, 'south': 40.30, 'east': 50.00, 'west': 49.75}
    },
    'gabala': {
        'name': 'Gabala',
        'country': 'Azerbaijan',
        'bbox': {'north': 40.95, 'south': 40.90, 'east': 47.90, 'west': 47.80}
    },
    'sheki': {
        'name': 'Sheki',
        'country': 'Azerbaijan',
        'bbox': {'north': 41.25, 'south': 41.15, 'east': 47.25, 'west': 47.10}
    },
    'ganja': {
        'name': 'Ganja',
        'country': 'Azerbaijan',
        'bbox': {'north': 40.75, 'south': 40.60, 'east': 46.45, 'west': 46.25}
    },
    'quba': {
        'name': 'Quba',
        'country': 'Azerbaijan',
        'bbox': {'north': 41.40, 'south': 41.30, 'east': 48.60, 'west': 48.45}
    },
    'lahij': {
        'name': 'Lahij',
        'country': 'Azerbaijan',
        'bbox': {'north': 40.90, 'south': 40.80, 'east': 48.45, 'west': 48.35}
    },
    'gobustan': {
        'name': 'Gobustan',
        'country': 'Azerbaijan',
        'bbox': {'north': 40.15, 'south': 40.05, 'east': 49.45, 'west': 49.35}
    },
    
    # --- GEORGIA ---
    'tbilisi': {
        'name': 'Tbilisi',
        'country': 'Georgia',
        'bbox': {'north': 41.80, 'south': 41.65, 'east': 44.90, 'west': 44.70}
    },
    'batumi': {
        'name': 'Batumi',
        'country': 'Georgia',
        'bbox': {'north': 41.70, 'south': 41.60, 'east': 41.70, 'west': 41.60}
    },
    'kazbegi': {
        'name': 'Kazbegi',
        'country': 'Georgia',
        'bbox': {'north': 42.70, 'south': 42.60, 'east': 44.70, 'west': 44.60}
    },
    'mtskheta': {
        'name': 'Mtskheta',
        'country': 'Georgia',
        'bbox': {'north': 41.85, 'south': 41.80, 'east': 44.75, 'west': 44.70}
    },
    'sighnaghi': {
        'name': 'Sighnaghi',
        'country': 'Georgia',
        'bbox': {'north': 41.65, 'south': 41.60, 'east': 46.00, 'west': 45.90}
    },
    'kutaisi': {
        'name': 'Kutaisi',
        'country': 'Georgia',
        'bbox': {'north': 42.30, 'south': 42.25, 'east': 42.75, 'west': 42.65}
    },
}
