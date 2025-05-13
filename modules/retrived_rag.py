from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

from underthesea import ner , pos_tag 
from itertools import groupby
import re 
from vncorenlp import VnCoreNLP
# Đường dẫn đến vector DB
INDEX_PATH = "C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/data/vector_db/faiss_index.index"
DOCMAP_PATH = "C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/data/vector_db/doc_map.pkl"

# Load vector DB, doc map, và model một lần
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
db = faiss.read_index(INDEX_PATH)
with open(DOCMAP_PATH, "rb") as f:
    doc_map = pickle.load(f)



# Tải VnCoreNLP model về và giải nén
# rdrsegmenter = VnCoreNLP("C:/Dungx/BAITAP_PYTHON/bt/ChuyenDe_HTTT/NBA-Search/model/VnCoreNLP/VnCoreNLP-1.2/VnCoreNLP-1.1.1.jar")

def extract_entities(text):
    tagged = pos_tag(text)
    proper_nouns = []
    current_entity = []

    for word, tag in tagged:
        if tag == 'Np':
            current_entity.append(word)
        elif current_entity:
            proper_nouns.append(" ".join(current_entity))
            current_entity = []
    if current_entity:
        proper_nouns.append(" ".join(current_entity))
    return proper_nouns



def extract_years(text):
    return re.findall(r'\b(19\d{2}|20\d{2})\b', text)

def retrieve_top_k(query, k):
    """
    Truy xuất top k văn bản gần nhất với truy vấn người dùng.
    
    Args:
        query (str): Câu hỏi hoặc truy vấn
        k (int): Số văn bản cần lấy 
    
    Returns:
        list: Danh sách văn bản (str) gần nhất
    """
    # Tạo embedding cho truy vấn
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    
    # Truy vấn FAISS
    distances, indices = db.search(query_embedding, k)
    
    # Lấy văn bản tương ứng
    return [doc_map[i] for i in indices[0] if i != -1 and i in doc_map]

def retrieve_entity(entity_list, year):
    all_results = []
    for entity in entity_list:
        query = f"Dữ liệu của {entity} "
        
        results = retrieve_top_k(query, k=5)
        print(f"Kết quả tìm được: {results}")
        all_results.append((entity, results))  # sửa ở đây
    return all_results

