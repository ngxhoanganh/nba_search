import pandas as pd
import os
import re

# Ánh xạ từ tiếng Việt sang cột dữ liệu
STAT_MAPPING = {
    "tuổi": "Age",
    "đội": "Team",
    "đội bóng": "Team",
    "vị trí": "Pos",
    "trận": "G",
    "số trận": "G",
    "trận đá chính": "GS",
    "phút thi đấu": "MP",
    "điểm": "PTS",
    "kiến tạo": "AST",
    "rebounds": "TRB",
    "bắt bóng bật bảng": "TRB",
    "reb tấn công": "ORB",
    "reb phòng ngự": "DRB",
    "cướp bóng": "STL",
    "chặn bóng": "BLK",
    "mất bóng": "TOV",
    "lỗi cá nhân": "PF",
    "ném thành công": "FG",
    "ném thực hiện": "FGA",
    "tỉ lệ ném": "FG%",
    "ném 3 điểm": "3P",
    "tỉ lệ 3 điểm": "3P%",
    "nỗ lực 3 điểm": "3PA",
    "ném 2 điểm": "2P",
    "nỗ lực 2 điểm": "2PA",
    "tỉ lệ 2 điểm": "2P%",
    "efg": "eFG%",
    "ném phạt": "FT",
    "nỗ lực ném phạt": "FTA",
    "tỉ lệ ném phạt": "FT%",
    "danh hiệu": "Awards",
}

TEAM_STAT_MAPPING = {
    "thắng": "W",
    "trận thắng": "W",
    "thua": "L",
    "trận thua": "L",
    "tỷ lệ thắng": "W/L%",
    "điểm ghi": "PS/G",
    "điểm thủng lưới": "PA/G",
    "srs": "SRS"
}
EXPANDED_STAT_MAPPING = {
    "thành tích tổng thể": "Overall",
    "thành tích" : "Overall",
    "thứ hạng": "Rk",
    "sân nhà": "Place Home",
    "sân khách": "Place Road",
    "miền đông": "Conference E",
    "miền tây": "Conference W",
    "sau all-star": "All-Star Post",
    "trước all-star": "All-Star Pre"
}
# player
def detect_stat_column(query):
    for vi, col in STAT_MAPPING.items():
        if vi in query:
            return col, vi
    return None, None
# conference
def detect_team_stat_column(query):
    for vi, col in TEAM_STAT_MAPPING.items():
        if vi in query:
            return col, vi
    return None, None
# expanded standing
def detect_expanded_stat_column(query):
    for vi, col in EXPANDED_STAT_MAPPING.items():
        if vi in query:
            return col, vi
    return None, None

def query_player_statistics(query: str):
    query = query.lower()
    data_dir = "data/Data_for_Rag"

    # Tìm năm
    year_match = re.search(r"\b(20\d{2})\b", query)
    if not year_match:
        return "Không xác định được năm trong truy vấn."
    year = year_match.group(1)

    # Đường dẫn tới file dữ liệu
    file_path = os.path.join(data_dir, f"rankPlayer/player_stats_{year}.csv")
    if not os.path.exists(file_path):
        return f"Không tìm thấy dữ liệu cầu thủ cho năm {year}."

    df = pd.read_csv(file_path)

    # Tìm tên cột và từ khóa tiếng Việt
    stat_col, stat_vi = detect_stat_column(query)
    if not stat_col:
        return "Không xác định được chỉ số thống kê trong truy vấn."

    # Truy vấn: top N
    match_top = re.search(r"top\s*(\d+)", query)
    
    top_n = 3  # Mặc định là top 3
    if match_top :
        if "cao" in query or "nhiều" in query or "lớn" in query or "to" in query:
            top_n = int(match_top.group(1))
            df_sorted = df.sort_values(by=stat_col, ascending=False).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Player']} - {row[stat_col]} {stat_vi}"
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} cầu thủ có {stat_vi} cao nhất năm {year}:\n" + "\n".join(results)
        if "thấp" in query or "ít" in query or "nhỏ" in query or "bé" in query:
            top_n = int(match_top.group(1))
            df_sorted = df.sort_values(by=stat_col, ascending=True).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Player']} - {row[stat_col]} {stat_vi}"
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} cầu thủ có {stat_vi} thấp nhất năm {year}:\n" + "\n".join(results)
    elif "nhất" in query:
        top_n = 3
        if "cao" in query or "nhiều" in query or "lớn" in query or "to" in query:
            df_sorted = df.sort_values(by=stat_col, ascending=False).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Player']} - {row[stat_col]} {stat_vi}"
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} cầu thủ có {stat_vi} cao nhất năm {year}:\n" + "\n".join(results)
        if "thấp" in query or "ít" in query or "nhỏ" in query or "bé" in query:
            df_sorted = df.sort_values(by=stat_col, ascending=True).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Player']} - {row[stat_col]} {stat_vi}"
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} cầu thủ có {stat_vi} thấp nhất năm {year}:\n" + "\n".join(results)
    # print("errorerror")
    

    # Truy vấn: tổng số
    if "tổng" in query:
        total = df[stat_col].sum()
        return f"Tổng {stat_vi} của tất cả cầu thủ trong năm {year} là {total}."

    # Truy vấn: trung bình
    if "trung bình" in query:
        avg = df[stat_col].mean()
        return f"Trung bình {stat_vi} của các cầu thủ năm {year} là {round(avg, 2)}."

    # Truy vấn: thông tin 1 cầu thủ cụ thể
    for player in df["Player"]:
        if player.lower() in query:
            row = df[df["Player"].str.lower() == player.lower()].iloc[0]
            return (
                f"Năm {year}, {row['Player']} ({row['Age']} tuổi) chơi cho {row['Team']} ở vị trí {row['Pos']}. "
                f"Thi đấu {row['G']} trận, trung bình {row['PTS']} điểm, {row['AST']} kiến tạo, "
                f"{row['TRB']} rebounds, {row['Awards']} danh hiệu."
            )

    return "Không tìm thấy cầu thủ hoặc loại truy vấn không được hỗ trợ. Yêu cầu người dùng hỏi lại rõ hơn."

def query_team_conference(query: str):

    
    # fix here



    query = query.lower()
    data_dir = "data/Data_for_Rag"

    # Tìm năm
    year_match = re.search(r"\b(20\d{2})\b", query)
    if not year_match:
        return "Không xác định được năm trong truy vấn."
    year = year_match.group(1)
    mien = ""
    # Xác định miền Đông hay miền Tây
    if "miền đông" in query:
        file_path = os.path.join(data_dir, f"BXH/Eastern_Conference_{year}.csv")
        mien = "miền đông"
    elif "miền tây" in query:
        file_path = os.path.join(data_dir, f"BXH/Western_Conference_{year}.csv")
        mien = "miền tây"
    else:
        return "Không xác định được miền Đông hay miền Tây trong truy vấn."

    if not os.path.exists(file_path):
        return f"Không tìm thấy dữ liệu cho miền tương ứng năm {year}."
    
    df = pd.read_csv(file_path)

    stat_col, stat_vi = detect_team_stat_column(query)

    if not stat_col:
        return "Không xác định được chỉ số thống kê trong truy vấn."

    match_top = re.search(r"top\s*(\d+)", query)
    top_n = 3  # Mặc định là top 3
    if match_top:
        if "cao" in query or "nhiều" in query or "lớn" in query or "to" in query:
            top_n = int(match_top.group(1))
            df_sorted = df.sort_values(by=stat_col, ascending=False).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Team']} - {row[stat_col]} {stat_vi}; "
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} đội có {stat_vi} cao nhất năm {year} ở {mien}:\n" + "\n".join(results)
        if "thấp" in query or "ít" in query or "nhỏ" in query or "bé" in query:
            top_n = int(match_top.group(1))
            df_sorted = df.sort_values(by=stat_col, ascending=True).head(top_n).reset_index(drop=True)
            results = [
                f"{i+1}. {row['Team']} - {row[stat_col]} {stat_vi}; "
                for i, row in df_sorted.iterrows()
            ]
            return f"Top {top_n} đội có {stat_vi} thấp nhất năm {year} ở {mien}:\n" + "\n".join(results)
    elif "nhất" in query:
            # Truy vấn: cao nhất / nhiều nhất
            if "cao" in query or "nhiều" in query or "lớn" in query or "to" in query:
                df_sorted = df.sort_values(by=stat_col, ascending=False).head(top_n).reset_index(drop=True)
                results = [
                    f"{i+1}. {row['Team']} - {row[stat_col]} {stat_vi}; "
                    for i, row in df_sorted.iterrows()
                ]
                return f"Top {top_n} đội có {stat_vi} cao nhất năm {year} ở {mien}:\n" + "\n".join(results)
            # Truy vấn: thấp nhất / ít nhất
            if "thấp" in query or "ít" in query or "nhỏ" in query or "bé" in query:
                df_sorted = df.sort_values(by=stat_col, ascending=True).head(top_n).reset_index(drop=True)
                results = [
                    f"{i+1}. {row['Team']} - {row[stat_col]} {stat_vi}; "
                    for i, row in df_sorted.iterrows()
                ]
                return f"Top {top_n} đội có {stat_vi} thấp nhất năm {year} ở {mien}:\n" + "\n".join(results)
    # Truy vấn đội cụ thể
    # for team in df["Team"].unique():
    #     if team.lower() in query:
    #         row = df[df["Team"].str.lower() == team.lower()].iloc[0]
    #         return (
    #             f"Năm {year}, đội {row['Team']} có {row['W']} trận thắng, "
    #             f"{row['L']} trận thua, tỷ lệ thắng {row['W/L%']}, "
    #             f"ghi trung bình {row['PS/G']} điểm mỗi trận, thủng lưới trung bình {row['PA/G']} điểm mỗi trận, "
    #             f"chỉ số SRS là {row['SRS']}."
    #         )

    # Truy vấn đội có thành tích cao nhất
    
    if "tổng" in query:
        total = df[stat_col].sum()
        return f"Tổng {stat_vi} của tất cả đội bóng trong năm {year} ở {mien} là {total}."
    if "trung bình" in query:
        avg = df[stat_col].mean()
        return f"Trung bình {stat_vi} của các đội bóng năm {year} ở {mien} là {round(avg, 2)}."
    return "Không xác định được đội hoặc truy vấn không phù hợp với bảng xếp hạng miền Đông/Tây."



def parse_win_percentage(value):
    if not isinstance(value, str):
        return 0
    try:
        # Xử lý dữ liệu kiểu ' 10 - 4' hoặc '15-16 hoặc '13–15' (dấu – Unicode)
        value = value.replace("–", "-")  # Unicode dash to regular
        value = re.sub(r"[^\d\-]", "", value)  # Xóa ký tự không cần thiết (như dấu ', khoảng trắng thừa,...)
        parts = value.strip().split("-")
        if len(parts) != 2:
            return 0
        wins, losses = map(int, parts)
        total = wins + losses
        return wins / total if total > 0 else 0
    except:
        return 0


def query_team_expanded_standing(query: str):
    query = query.lower()
    data_dir = "data/Data_for_Rag"

    # Tìm năm trong câu truy vấn
    year_match = re.search(r"\b(20\d{2})\b", query)
    if not year_match:
        return "Không xác định được năm trong truy vấn."
    year = year_match.group(1)

    # Xác định tệp dữ liệu
    file_path = os.path.join(data_dir, f"BXH/Expanded_Standings_{year}.xlsx")
    if not os.path.exists(file_path):
        return f"Không tìm thấy dữ liệu đội bóng cho năm {year}."

    df = pd.read_excel(file_path)

    # Tìm thuộc tính cần truy vấn (vd: sân nhà, tổng thể, miền tây,...)
    selected_stat = None
    for key in EXPANDED_STAT_MAPPING:
        if key in query:
            selected_stat = EXPANDED_STAT_MAPPING[key]
            break

    if not selected_stat:
        return "Không xác định được chỉ số thống kê trong truy vấn."

    # Kiểm tra nếu là cột dạng "x - y" cần chuyển thành tỉ lệ
    if selected_stat in ["Place Home", "Place Road", "Conference E", "Conference W", "All-Star Pre", "All-Star Post"]:
        df["WinRate"] = df[selected_stat].apply(parse_win_percentage)
        df_sorted = df.sort_values("WinRate", ascending=False)
    else:
        # Nếu là số hạng thì sắp xếp tăng (hạng 1 là tốt nhất), còn lại sắp giảm
        if selected_stat == "Rk":
            df_sorted = df.sort_values(selected_stat, ascending=True)
        else:
            df_sorted = df.sort_values(selected_stat, ascending=False)

    # Xác định top N (mặc định top 5)
    top_match = re.search(r"top\s*(\d+)", query)
    top_n = int(top_match.group(1)) if top_match else 5

    result_rows = []
    for i, row in df_sorted.head(top_n).iterrows():
        if selected_stat in df.columns:
            value = row[selected_stat]
        else:
            value = f"{row['WinRate']*100:.1f}%"
        result_rows.append(f"{row['Team']}: {value}")

    stat_name_vi = [k for k, v in EXPANDED_STAT_MAPPING.items() if v == selected_stat][0]
    return f"Top {top_n} đội có {stat_name_vi} tốt nhất năm {year}:\n" + "\n".join(result_rows)


    # Truy vấn top đội ở miền Đông / Tây
    
    


