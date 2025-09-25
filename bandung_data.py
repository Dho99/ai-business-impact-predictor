"""
Bandung Kecamatan Data Module

Contains demographic and infrastructure data for all kecamatan in Bandung City.
"""

import pandas as pd

def get_bandung_kecamatan_data():
    """
    Returns demographic and infrastructure data for all kecamatan in Bandung.
    
    Returns:
        dict: Dictionary with kecamatan names as keys and demographic data as values
    """
    # Data kecamatan Bandung dari dataset training
    kecamatan_data = {
        'andir': {
            'name': 'Andir',
            'population': 99119,
            'area_km2': 4.22,
            'density': 23488,
            'malls': 1.0,
            'minimarkets': 20.0,
            'parks': 34.0,
            'description': 'Area dengan kepadatan tinggi, infrastruktur sedang'
        },
        'antapani': {
            'name': 'Antapani',
            'population': 80530,
            'area_km2': 4.22,
            'density': 19083,
            'malls': 3.05,
            'minimarkets': 21.0,
            'parks': 68.0,
            'description': 'Area residensial dengan banyak taman'
        },
        'arcamanik': {
            'name': 'Arcamanik',
            'population': 80387,
            'area_km2': 7.59,
            'density': 10591,
            'malls': 3.05,
            'minimarkets': 13.0,
            'parks': 77.0,
            'description': 'Area luas dengan kepadatan sedang, banyak ruang hijau'
        },
        'astanaanyar': {
            'name': 'Astanaanyar',
            'population': 73232,
            'area_km2': 2.68,
            'density': 27325,
            'malls': 3.05,
            'minimarkets': 20.0,
            'parks': 15.0,
            'description': 'Area sangat padat dengan infrastruktur terbatas'
        },
        'babakan_ciparay': {
            'name': 'Babakan Ciparay',
            'population': 143651,
            'area_km2': 7.07,
            'density': 20318,
            'malls': 1.0,
            'minimarkets': 17.0,
            'parks': 13.0,
            'description': 'Area populasi besar dengan infrastruktur terbatas'
        },
        'bandung_kidul': {
            'name': 'Bandung Kidul',
            'population': 61419,
            'area_km2': 5.42,
            'density': 11332,
            'malls': 3.05,
            'minimarkets': 9.0,
            'parks': 53.0,
            'description': 'Area selatan Bandung dengan banyak taman'
        },
        'bandung_kulon': {
            'name': 'Bandung Kulon',
            'population': 136622,
            'area_km2': 6.95,
            'density': 19658,
            'malls': 3.05,
            'minimarkets': 20.0,
            'parks': 15.0,
            'description': 'Area barat Bandung dengan populasi besar'
        },
        'bandung_wetan': {
            'name': 'Bandung Wetan',
            'population': 28848,
            'area_km2': 3.44,
            'density': 8386,
            'malls': 4.0,
            'minimarkets': 14.0,
            'parks': 117.0,
            'description': 'Area tengah kota dengan banyak fasilitas dan taman'
        },
        'batununggal': {
            'name': 'Batununggal',
            'population': 121469,
            'area_km2': 4.82,
            'density': 25201,
            'malls': 4.0,
            'minimarkets': 17.0,
            'parks': 19.0,
            'description': 'Area padat dengan infrastruktur baik'
        },
        'bojongloa_kaler': {
            'name': 'Bojongloa Kaler',
            'population': 124323,
            'area_km2': 3.12,
            'density': 39847,
            'malls': 3.05,
            'minimarkets': 13.0,
            'parks': 34.0,
            'description': 'Area dengan kepadatan tertinggi di Bandung'
        },
        'bojongloa_kidul': {
            'name': 'Bojongloa Kidul',
            'population': 87988,
            'area_km2': 5.2,
            'density': 16921,
            'malls': 3.05,
            'minimarkets': 16.0,
            'parks': 15.0,
            'description': 'Area selatan dengan kepadatan sedang'
        },
        'buahbatu': {
            'name': 'Buahbatu',
            'population': 104434,
            'area_km2': 7.46,
            'density': 13999,
            'malls': 2.0,
            'minimarkets': 36.0,
            'parks': 90.0,
            'description': 'Area berkembang dengan banyak minimarket dan taman'
        },
        'cibeunying_kaler': {
            'name': 'Cibeunying Kaler',
            'population': 70662,
            'area_km2': 4.64,
            'density': 15229,
            'malls': 3.05,
            'minimarkets': 34.0,
            'parks': 31.0,
            'description': 'Area utara dengan akses retail baik'
        },
        'cibeunying_kidul': {
            'name': 'Cibeunying Kidul',
            'population': 113535,
            'area_km2': 4.14,
            'density': 27424,
            'malls': 3.05,
            'minimarkets': 17.0,
            'parks': 16.0,
            'description': 'Area padat dekat pusat kota'
        },
        'cibiru': {
            'name': 'Cibiru',
            'population': 76236,
            'area_km2': 6.84,
            'density': 11146,
            'malls': 3.05,
            'minimarkets': 7.0,
            'parks': 8.0,
            'description': 'Area pinggiran dengan infrastruktur minimal'
        },
        'cicendo': {
            'name': 'Cicendo',
            'population': 96382,
            'area_km2': 7.79,
            'density': 12373,
            'malls': 2.0,
            'minimarkets': 35.0,
            'parks': 46.0,
            'description': 'Area komersial dengan banyak minimarket'
        },
        'cidadap': {
            'name': 'Cidadap',
            'population': 54680,
            'area_km2': 8.42,
            'density': 6494,
            'malls': 3.05,
            'minimarkets': 10.0,
            'parks': 8.0,
            'description': 'Area utara dengan kepadatan rendah'
        },
        'cinambo': {
            'name': 'Cinambo',
            'population': 25585,
            'area_km2': 4.25,
            'density': 6020,
            'malls': 3.05,
            'minimarkets': 3.0,
            'parks': 7.0,
            'description': 'Area pinggiran dengan infrastruktur terbatas'
        },
        'coblong': {
            'name': 'Coblong',
            'population': 115273,
            'area_km2': 7.31,
            'density': 15769,
            'malls': 3.05,
            'minimarkets': 62.0,
            'parks': 37.0,
            'description': 'Area premium dengan akses retail terbaik'
        },
        'gedebage': {
            'name': 'Gedebage',
            'population': 42071,
            'area_km2': 9.96,
            'density': 4224,
            'malls': 3.05,
            'minimarkets': 9.0,
            'parks': 47.0,
            'description': 'Area industri dengan kepadatan rendah'
        },
        'kiaracondong': {
            'name': 'Kiaracondong',
            'population': 131413,
            'area_km2': 5.8,
            'density': 22657,
            'malls': 1.0,
            'minimarkets': 36.0,
            'parks': 17.0,
            'description': 'Area padat dengan banyak minimarket'
        },
        'lengkong': {
            'name': 'Lengkong',
            'population': 71000,
            'area_km2': 5.91,
            'density': 12014,
            'malls': 3.05,
            'minimarkets': 43.0,
            'parks': 41.0,
            'description': 'Area tengah dengan infrastruktur seimbang'
        },
        'mandalajati': {
            'name': 'Mandalajati',
            'population': 73956,
            'area_km2': 4.8,
            'density': 15408,
            'malls': 3.05,
            'minimarkets': 16.0,
            'parks': 21.0,
            'description': 'Area residensial dengan fasilitas standar'
        },
        'panyileukan': {
            'name': 'Panyileukan',
            'population': 40772,
            'area_km2': 5.31,
            'density': 7678,
            'malls': 3.05,
            'minimarkets': 9.0,
            'parks': 53.0,
            'description': 'Area pinggiran dengan banyak ruang hijau'
        },
        'rancasari': {
            'name': 'Rancasari',
            'population': 86725,
            'area_km2': 7.01,
            'density': 12372,
            'malls': 3.05,
            'minimarkets': 21.0,
            'parks': 50.0,
            'description': 'Area berkembang dengan fasilitas memadai'
        },
        'regol': {
            'name': 'Regol',
            'population': 80609,
            'area_km2': 4.74,
            'density': 17006,
            'malls': 2.0,
            'minimarkets': 40.0,
            'parks': 15.0,
            'description': 'Area komersial dengan banyak toko'
        },
        'sukajadi': {
            'name': 'Sukajadi',
            'population': 103066,
            'area_km2': 5.28,
            'density': 19520,
            'malls': 3.05,
            'minimarkets': 33.0,
            'parks': 29.0,
            'description': 'Area premium utara Bandung'
        },
        'sukasari': {
            'name': 'Sukasari',
            'population': 77576,
            'area_km2': 6.36,
            'density': 12197,
            'malls': 2.0,
            'minimarkets': 28.0,
            'parks': 23.0,
            'description': 'Area utara dengan fasilitas baik'
        },
        'sumur_bandung': {
            'name': 'Sumur Bandung',
            'population': 38323,
            'area_km2': 3.49,
            'density': 10981,
            'malls': 4.0,
            'minimarkets': 19.0,
            'parks': 38.0,
            'description': 'Area pusat kota dengan infrastruktur lengkap'
        },
        'ujung_berung': {
            'name': 'Ujung Berung',
            'population': 90562,
            'area_km2': 6.24,
            'density': 14513,
            'malls': 3.05,
            'minimarkets': 24.0,
            'parks': 9.0,
            'description': 'Area timur Bandung dengan infrastruktur standar'
        }
    }
    
    return kecamatan_data

def get_kecamatan_options():
    """
    Returns list of kecamatan options for selectbox.
    
    Returns:
        list: List of tuples (key, display_name)
    """
    kecamatan_data = get_bandung_kecamatan_data()
    return [(key, data['name']) for key, data in kecamatan_data.items()]

def get_kecamatan_info(kecamatan_key):
    """
    Get detailed info for specific kecamatan.
    
    Args:
        kecamatan_key (str): Kecamatan key
        
    Returns:
        dict: Kecamatan data or None if not found
    """
    kecamatan_data = get_bandung_kecamatan_data()
    return kecamatan_data.get(kecamatan_key)