import io
from typing import List, Dict

import pandas as pd
import streamlit as st
import stanza
from docx import Document


st.set_page_config(
    page_title="POS Tagging Bahasa Indonesia",
    page_icon="🧠",
    layout="wide",
)

UPOS_DESCRIPTIONS = {
    "ADJ": "Adjektiva",
    "ADP": "Adposisi",
    "ADV": "Adverbia",
    "AUX": "Auxiliary",
    "CCONJ": "Konjungsi koordinatif",
    "DET": "Determiner",
    "INTJ": "Interjeksi",
    "NOUN": "Nomina",
    "NUM": "Numeralia",
    "PART": "Partikel",
    "PRON": "Pronomina",
    "PROPN": "Nama diri",
    "PUNCT": "Tanda baca",
    "SCONJ": "Konjungsi subordinatif",
    "SYM": "Simbol",
    "VERB": "Verba",
    "X": "Lainnya",
}


@st.cache_resource(show_spinner=False)
def load_pipeline():
    """Load Indonesian Stanza pipeline once per session/server."""
    try:
        stanza.download("id", verbose=False)
    except Exception:
        # Safe fallback if model already exists or there is a temporary download message.
        pass

    return stanza.Pipeline(
        lang="id",
        processors="tokenize,pos",
        use_gpu=False,
        verbose=False,
    )


def read_txt(uploaded_file) -> str:
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")



def read_docx(uploaded_file) -> str:
    data = io.BytesIO(uploaded_file.getvalue())
    doc = Document(data)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)



def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return read_txt(uploaded_file)
    if name.endswith(".docx"):
        return read_docx(uploaded_file)
    raise ValueError("Format file belum didukung. Gunakan .txt atau .docx")



def tag_text(nlp, text: str) -> pd.DataFrame:
    doc = nlp(text)
    rows: List[Dict] = []

    for sent_idx, sent in enumerate(doc.sentences, start=1):
        for word_idx, word in enumerate(sent.words, start=1):
            rows.append(
                {
                    "sentence_id": sent_idx,
                    "token_id": word_idx,
                    "token": word.text,
                    "lemma": getattr(word, "lemma", None),
                    "upos": getattr(word, "upos", None),
                    "xpos": getattr(word, "xpos", None),
                    "feats": getattr(word, "feats", None),
                }
            )

    return pd.DataFrame(rows)



def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")



def main():
    st.title("POS Tagging Dokumen Bahasa Indonesia")
    st.caption(
        "Aplikasi ini melakukan part-of-speech tagging pada teks bahasa Indonesia menggunakan Stanza."
    )

    with st.expander("Tentang output", expanded=False):
        st.markdown(
            """
            - **UPOS**: universal part-of-speech tag.
            - **XPOS**: tag tambahan spesifik model/treebank.
            - **UFeats**: fitur morfologis jika tersedia.
            - File yang didukung saat ini: **.txt** dan **.docx**.
            """
        )

    nlp = load_pipeline()

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Unggah dokumen", type=["txt", "docx"], help="Unggah file .txt atau .docx"
        )

    with col2:
        st.markdown("**Atau tempelkan teks langsung**")
        manual_text = st.text_area(
            "Masukkan teks bahasa Indonesia",
            value="Pemerintah sedang mendorong transformasi digital di berbagai sektor.",
            height=180,
        )

    source_text = ""
    source_label = ""

    if uploaded_file is not None:
        try:
            source_text = extract_text(uploaded_file)
            source_label = f"File: {uploaded_file.name}"
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            st.stop()
    else:
        source_text = manual_text.strip()
        source_label = "Input manual"

    analyze = st.button("Proses POS Tagging", type="primary", use_container_width=True)

    if analyze:
        if not source_text.strip():
            st.warning("Teks masih kosong. Silakan unggah dokumen atau isi teks terlebih dahulu.")
            st.stop()

        with st.spinner("Sedang melakukan POS tagging..."):
            df = tag_text(nlp, source_text)

        if df.empty:
            st.warning("Tidak ada token yang berhasil diproses.")
            st.stop()

        st.success(f"Analisis selesai dari sumber: {source_label}")

        total_tokens = len(df)
        total_sentences = int(df["sentence_id"].max()) if not df.empty else 0
        unique_upos = df["upos"].nunique(dropna=True)

        met1, met2, met3 = st.columns(3)
        met1.metric("Jumlah token", total_tokens)
        met2.metric("Jumlah kalimat", total_sentences)
        met3.metric("Jenis tag UPOS", unique_upos)

        tab1, tab2, tab3 = st.tabs(["Hasil tagging", "Distribusi tag", "Legenda UPOS"])

        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button(
                label="Unduh hasil CSV",
                data=convert_df_to_csv(df),
                file_name="hasil_pos_tagging_indonesia.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with tab2:
            pos_counts = df["upos"].fillna("UNKNOWN").value_counts().rename_axis("upos").reset_index(name="jumlah")
            st.dataframe(pos_counts, use_container_width=True)
            chart_df = pos_counts.set_index("upos")
            st.bar_chart(chart_df)

        with tab3:
            legend_df = pd.DataFrame(
                [{"upos": k, "deskripsi": v} for k, v in UPOS_DESCRIPTIONS.items()]
            )
            st.dataframe(legend_df, use_container_width=True)

        with st.expander("Preview teks sumber", expanded=False):
            st.text(source_text[:4000])


if __name__ == "__main__":
    main()
