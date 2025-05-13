from inference.inference_network import InferenceNetwork
import google.generativeai as genai
from modules.retrived_rag import retrieve_top_k, retrieve_entity, extract_entities, extract_years
from modules.retrived_top import query_player_statistics, query_team_expanded_standing,query_team_conference 
class Query(object):

    def __init__(self, query):
        self.text = query

    # Method to process query 
    def process(self):
        network = InferenceNetwork(self.text)
        return network.response()
    def classify_query(self, query):
        genai.configure(api_key="AIzaSyARsx4RDoObhkrUvYxf8fjLtX-NlH9UlaY")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        prompt = f"""
            Bạn là một hệ thống phân loại câu hỏi về bóng đá thành 3 loại:

            1. "normal" – Câu hỏi thông tin đơn lẻ về người, đội, thời gian, địa điểm...
            Ví dụ: 
            - "Ronaldo sinh năm bao nhiêu?"
            - "Messi đang chơi cho đội nào?"
            - "Thành tích sân nhà của Real trong năm 2023"
            

            2. "compare" – Câu hỏi yêu cầu so sánh giữa hai hoặc nhiều đối tượng.
            Ví dụ: 
            - "So sánh Messi và Ronaldo"
            - "Đội bóng nào mạnh hơn, Brazil hay Argentina?"

            3. "ranking" – Câu hỏi yêu cầu thống kê, tổng hợp, xếp hạng.
            Ví dụ: 
            - "Top 3 cầu thủ ghi bàn nhiều nhất"
            - "Đội nào vô địch Euro nhiều nhất?"
            - "Tổng số bàn thắng của Haaland năm 2023?"
            - "Ai là cầu thủ có nhiều danh hiệu nhất?"

            Hãy phân loại truy vấn sau và chỉ trả về duy nhất 1 trong 3 từ: normal, compare, ranking.

            Truy vấn: "{query}"
            """
        response = model.generate_content(prompt)
        return response.text.strip().lower()
   
    # def process_API_NLP(self):
    #     genai.configure(api_key="AIzaSyARsx4RDoObhkrUvYxf8fjLtX-NlH9UlaY")
    #     model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
        
    #     response = model.generate_content(self.text)
    #     return response.text
    
    def process_RAG(self):
        retrieved_texts = retrieve_top_k(self.text, k=3)
        # truy vấn theo thực thể 
        genai.configure(api_key="AIzaSyARsx4RDoObhkrUvYxf8fjLtX-NlH9UlaY")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
        # Tạo prompt từ context và truy vấn
        prompt = f"""Bạn là một chatbot hỏi đáp về chủ đề bóng rổ. Dựa trên kiến thức của bạn và những thông tin được cung cấp sau , hãy trả lời câu hỏi một cách chính xác, rõ ràng:

        {retrieved_texts}

        Câu hỏi: {self.text}
        """
        response = model.generate_content(prompt)
        return response.text 
    def process_compare(self):
        # Truy vấn theo thực thể 
        retrieved_texts = retrieve_top_k(self.text, k=5)
        entity = extract_entities(self.text)
        years = extract_years(self.text)
        year = years[0] if years else None  # Lấy năm đầu tiên
        data_entity = retrieve_entity(entity, year)
       
        genai.configure(api_key="AIzaSyARsx4RDoObhkrUvYxf8fjLtX-NlH9UlaY")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
        # Tạo prompt từ context và truy vấn
        prompt = f"""Bạn là một chatbot hỏi đáp về chủ đề bóng rổ. Dựa trên kiến thức của bạn và những thông tin được cung cấp sau , hãy trả lời câu hỏi một cách chính xác, rõ ràng:

        {data_entity, retrieved_texts}

        Câu hỏi: {self.text}
        """
        response = model.generate_content(prompt)
        # return "Đây là câu hỏi so sánh: "+response.text +"Danh sách thực thể : "+str(entity) 
        return "Đây là câu hỏi so sánh: "+response.text 
    def process_Top(self):
        info = ""
        self.text = self.text.lower()
        if "đội" in self.text or "câu lạc bộ" in self.text or "clb" in self.text or "team" in self.text:
            if "miền đông" in self.text or "miền tây" in self.text or "west" in self.text or "east" in self.text:
                info = " bảng  conference: "+query_team_conference(self.text)
            else:
                info = " bảng  extend : "+query_team_expanded_standing(self.text)

            
            # return info
        elif "cầu thủ" in self.text or "người" in self.text:

            info = query_player_statistics(self.text)
        genai.configure(api_key="AIzaSyARsx4RDoObhkrUvYxf8fjLtX-NlH9UlaY")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
            # Tạo prompt từ context và truy vấn
        prompt = f"""Bạn là một chatbot hỏi đáp về chủ đề bóng rổ. Dựa trên kiến thức của bạn và những thông tin được cung cấp sau , hãy trả lời câu hỏi một cách chính xác, rõ ràng:

            {info}

            Câu hỏi: {self.text}
            """
        response = model.generate_content(prompt)
        response = "Đây là câu hỏi thống kê :" + response.text
        return response
        # return "Đây là câu hỏi thống kê : "+info