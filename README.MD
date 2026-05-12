# IndoTagger

IndoTagger adalah aplikasi berbasis web yang digunakan untuk melakukan *Part-of-Speech (POS) Tagging* pada teks bahasa Indonesia. Aplikasi ini dibangun menggunakan **Streamlit** dan memanfaatkan library **Stanza** untuk melakukan analisis linguistik secara otomatis. Hasil analisis dapat ditampilkan dalam bentuk tabel, distribusi tag, dan diunduh dalam format CSV.

---

## Fitur Utama

- Input teks secara manual
- Upload dokumen `.txt` dan `.docx`
- POS Tagging bahasa Indonesia
- Menampilkan:
  - Token
  - Lemma
  - UPOS
  - XPOS
  - Fitur morfologis
- Visualisasi distribusi tag
- Export hasil ke CSV

---

## Teknologi yang Digunakan

- Python
- Streamlit
- Stanza
- Pandas
- python-docx

---

## Struktur Folder

```text
indotagger/
├── venv/
├── streamlit_pos_tagger_id.py
├── requirements.txt
└── README.md