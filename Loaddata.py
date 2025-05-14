import os
import pickle
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import re
import unicodedata
from docx import Document
# Đường dẫn thư mục
MODEL_FOLDER = "C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/data/vector_db"
INDEX_PATH = os.path.join(MODEL_FOLDER, "faiss_index.index")
DOCMAP_PATH = os.path.join(MODEL_FOLDER, "doc_map.pkl")
CSV_BASE_FOLDER = "C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/data/Data_for_Rag"  # Thư mục gốc chứa các thư mục con
YEARS = [2021, 2022, 2023, 2024, 2025]  # Các năm cần đọc

# Đường dẫn đến các thư mục con
BXH_FOLDER = os.path.join(CSV_BASE_FOLDER, "BXH")
CONFRONTATION_FOLDER = os.path.join(CSV_BASE_FOLDER, "confrontation")
PLAYER_FOLDER = os.path.join(CSV_BASE_FOLDER, "rankPlayer")

# Load model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Hàm tạo văn bản mô tả từ DataFrame + Năm (cho dữ liệu cầu thủ)
def create_documents(dfs, years):
    documents = []
    doc_table_map = {}
    for df, year in zip(dfs, years):
        for _, row in df.iterrows():
            text = (
                f"Năm {year}, {row['Player']} ({row['Age']} tuổi) chơi cho {row['Team']} ở vị trí {row['Pos']}. "
                f"Thi đấu {row['G']} trận, trung bình {row['PTS']} điểm, {row['AST']} kiến tạo, "
                f"{row['TRB']} rebounds, {row['Awards']} danh hiệu."
            )
            chunks = chunk_text(text, chunk_size=50)
            for chunk in chunks:
                doc_index = len(documents)
                documents.append(chunk)
                doc_table_map[doc_index] = f"player_stats_{year}.csv"
    return documents, doc_table_map

# Hàm tạo văn bản mô tả từ DataFrame + Năm (cho bảng xếp hạng và mở rộng)
def create_bxh_documents(dfs_eastern, dfs_western, dfs_expanded, years):
    documents = []
    doc_table_map = {}
    # Xử lý Eastern Conference
    for df, year in zip(dfs_eastern, years):
        for _, row in df.iterrows():
            team = row['Team']
            if pd.notna(team):  # Kiểm tra giá trị không phải NaN
                text = (
                    f"Năm {year}, đội {team} có {row['W']} trận thắng, "
                    f"{row['L']} trận thua, tỷ lệ thắng {row['W/L%']}, "
                    f"ghi trung bình {row['PS/G']} điểm mỗi trận, thủng lưới trung bình {row['PA/G']} điểm mỗi trận, "
                    f"chỉ số SRS là {row['SRS']}."
                )
                chunks = chunk_text(text, chunk_size=50)
                for chunk in chunks:
                    doc_index = len(documents)
                    documents.append(chunk)
                    doc_table_map[doc_index] = f"Eastern_Conference{year}.csv"

    # Xử lý Western Conference
    for df, year in zip(dfs_western, years):
        for _, row in df.iterrows():
            team = row['Team']
            if pd.notna(team):  # Kiểm tra giá trị không phải NaN
                text = (
                    f"Năm {year}, đội {team} có {row['W']} trận thắng, "
                    f"{row['L']} trận thua, tỷ lệ thắng {row['W/L%']}, "
                    f"ghi trung bình {row['PS/G']} điểm mỗi trận, thủng lưới trung bình {row['PA/G']} điểm mỗi trận, "
                    f"chỉ số SRS là {row['SRS']}."
                )
                chunks = chunk_text(text, chunk_size=50)
                for chunk in chunks:
                    doc_index = len(documents)
                    documents.append(chunk)
                    doc_table_map[doc_index] = f"Western_Conference{year}.csv"

    # Xử lý Expanded Standings
    for df, year in zip(dfs_expanded, years):
        for _, row in df.iterrows():
            text = (
                f"Năm {year}, đội {row['Team']} đạt thành tích tổng thể {row['Overall']}. "
                f"Thứ hạng (Rank) {row['Rk']}."
                f"Thành tích sân nhà: {row['Place Home']}, sân khách: {row['Place Road']}. "
                f"Thành tích theo khu vực: miền Đông {row['Conference E']}, miền Tây {row['Conference W']}. "
                f"Điểm đáng chú ý: sau All-Star {row['All-Star Post']}, trước All-Star {row['All-Star Pre']}."
            )
            chunks = chunk_text(text, chunk_size=50)
            for chunk in chunks:
                    doc_index = len(documents)
                    documents.append(chunk)
                    doc_table_map[doc_index] = f"Expanded_Standings{year}.xlsx"
    return documents, doc_table_map

# Hàm tạo văn bản mô tả từ DataFrame + Năm (cho dữ liệu đối đầu)
def create_confrontation_documents(dfs_confrontation, years):
    documents = []
    doc_table_map = {}
    for df, year in zip(dfs_confrontation, years):
        for _, row in df.iterrows():
            team = row['Team']
            text = f"Năm {year}, thành tích đối đầu của đội {team}: "
            results = []
            for opponent, result in row.items():
                if opponent not in ['Rk', 'Team'] and not pd.isna(result):
                    results.append(f"{opponent} ({result.strip()})")
            text += ", ".join(results) + "."
            chunks = chunk_text(text, chunk_size=50)
            for chunk in chunks:
                    doc_index = len(documents)
                    documents.append(chunk)
                    doc_table_map[doc_index] = f"Team_vs_Team{year}.csv"
    return documents, doc_table_map

def chunk_text(text, chunk_size=50):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Load hoặc tạo mới
if os.path.exists(INDEX_PATH) and os.path.exists(DOCMAP_PATH):
    print("✅ Đang load FAISS index và doc_map từ file...")
    index = faiss.read_index(INDEX_PATH)
    with open(DOCMAP_PATH, "rb") as f:
        doc_map = pickle.load(f)
else:
    print("⚙️ Chưa có dữ liệu, tạo mới FAISS index...")
    
    # Đọc dữ liệu từ các thư mục con
    dfs_players = []  # Dữ liệu cầu thủ
    dfs_eastern = []  # Dữ liệu Eastern Conference
    dfs_western = []  # Dữ liệu Western Conference
    dfs_expanded = []  # Dữ liệu Expanded Standings
    dfs_confrontation = []  # Dữ liệu Team vs Team

    for year in YEARS:
        # Đọc dữ liệu cầu thủ (CSV)
        player_file = os.path.join(PLAYER_FOLDER, f"player_stats_{year}.csv")
        if os.path.exists(player_file):
            dfs_players.append(pd.read_csv(player_file))
        else:
            print(f"⚠️ Không tìm thấy file: {player_file}")

        # Đọc dữ liệu Eastern Conference (CSV)
        eastern_file = os.path.join(BXH_FOLDER, f"Eastern_Conference_{year}.csv")
        if os.path.exists(eastern_file):
            dfs_eastern.append(pd.read_csv(eastern_file))
        else:
            print(f"⚠️ Không tìm thấy file: {eastern_file}")

        # Đọc dữ liệu Western Conference (CSV)
        western_file = os.path.join(BXH_FOLDER, f"Western_Conference_{year}.csv")
        if os.path.exists(western_file):
            dfs_western.append(pd.read_csv(western_file))
        else:
            print(f"⚠️ Không tìm thấy file: {western_file}")

        # Đọc dữ liệu Expanded Standings (Excel)
        expanded_file = os.path.join(BXH_FOLDER, f"Expanded_Standings_{year}.xlsx")
        if os.path.exists(expanded_file):
            dfs_expanded.append(pd.read_excel(expanded_file))
        else:
            print(f"⚠️ Không tìm thấy file: {expanded_file}")

        # Đọc dữ liệu Team vs Team (CSV)
        confrontation_file = os.path.join(CONFRONTATION_FOLDER, f"Team_vs_Team_{year}.csv")
        if os.path.exists(confrontation_file):
            dfs_confrontation.append(pd.read_csv(confrontation_file))
        else:
            print(f"⚠️ Không tìm thấy file: {confrontation_file}")

    def create_history_documents(docx_path, min_length=30):
        """
        Đọc và tiền xử lý nội dung file docx về lịch sử giải đấu.

        Args:
            docx_path (str): Đường dẫn tới file .docx.
            min_length (int): Độ dài tối thiểu để giữ lại đoạn văn.

        Returns:
            list[str]: Danh sách các đoạn văn bản đã được làm sạch.
        """
        doc = Document(docx_path)
        paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

        clean_paragraphs = []

        for para in paragraphs:
            # Loại bỏ các đoạn chỉ có số, ký tự đầu dòng, hoặc quá ngắn
            if len(para) < min_length:
                continue
            # Loại các dấu xuống dòng hoặc khoảng trắng dư
            para = re.sub(r'\s+', ' ', para)
            # Bỏ các bullet đầu dòng (•, -, etc.)
            para = re.sub(r'^[-•\d\.\s]+', '', para)
            clean_paragraphs.append(para)

        return clean_paragraphs


    # Tạo documents từ dữ liệu
    documents1, doc_map1 = create_documents(dfs_players, YEARS)
    documents2,  doc_map2 = create_bxh_documents(dfs_eastern, dfs_western, dfs_expanded, YEARS)
    documents3,  doc_map3 = create_confrontation_documents(dfs_confrontation, YEARS)
    documents4 = create_history_documents("C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/data/Data_for_Rag/history.docx")
    documents = documents1 + documents2 + documents3+ documents4
    doc_table_map = {**doc_map1, **doc_map2, **doc_map3}
    # Chia nhỏ văn bản thành các đoạn nhỏ hơn
    # documents = [chunk for doc in documents for chunk in chunk_text(doc, chunk_size=50)]
    embeddings = model.encode(documents)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    doc_map = {i: doc for i, doc in enumerate(documents)}

    # Lưu lại
    TABLEMAP_PATH = os.path.join(MODEL_FOLDER, "doc_table_map.pkl")

    with open(TABLEMAP_PATH, "wb") as f:
        pickle.dump(doc_table_map, f)
    faiss.write_index(index, INDEX_PATH)
    with open(DOCMAP_PATH, "wb") as f:
        pickle.dump(doc_map, f)
    print("✅ Đã tạo và lưu FAISS index + doc_map.")
