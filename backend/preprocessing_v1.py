import pandas as pd
import json
import os

# 파일 경로 설정 (구조에 맞게)
INPUT_PATH = './data/raw/timetable.csv'
OUTPUT_DIR = './data/processed/'

def time_str_to_seconds(t_str):
    """
    문자열 시간('HH:MM:SS')을 자정 기준 초(int)로 변환
    예: '12:00:00' -> 43200, '25:00:00' -> 90000
    """
    try:
        h, m, s = map(int, t_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return None

def preprocess_timetable():
    # 1. CSV 읽기 (인코딩 주의: 한글 깨짐 방지 cp949 또는 utf-8)
    print("CSV 로딩 중...")
    df = pd.read_csv(INPUT_PATH, encoding='EUC-KR', dtype={'역사코드': str, '호선': str})
    
    # 2. 데이터 전처리
    # 2-1. 시간 변환 (벡터 연산 적용을 위해 apply 사용)
    df['arr_sec'] = df['열차도착시간'].apply(time_str_to_seconds)
    df['dept_sec'] = df['열차출발시간'].apply(time_str_to_seconds)
    df['arr_sec'] = df['arr_sec'].fillna(df['dept_sec'])
    # 결측치는 0이 아닌 출발시간으로 대체. 결국 출발시간 이전에만 도착하면 되니까.
    # .fillna() : fill+na(Not Available) -> 결측치(NaN)를 채운다는 의미.

    # 2-2. 정렬 (핵심 로직: 사용자 코드의 아이디어)
    # 같은 열차끼리 묶고, 시간순으로 나열해야 A역 -> B역 연결 고리가 보임
    df = df.sort_values(by=['주중주말', '열차코드', 'arr_sec'])

    # 3. 다음 역 정보 가져오기 (Pandas Shift 기법 - for문 대체)
    # 다음 행의 정보를 현재 행의 'next_' 컬럼으로 가져옴
    df['next_station_code'] = df['역사코드'].shift(-1)
    df['next_station_name'] = df['역사명'].shift(-1)
    df['next_arr_sec'] = df['arr_sec'].shift(-1)
    df['next_train_code'] = df['열차코드'].shift(-1)
    
    # 4. 유효한 간선(Edge) 필터링
    # 조건: 현재 행의 열차코드와 다음 행의 열차코드가 같아야 함 (다르면 종착역임)
    valid_edges = df[df['열차코드'] == df['next_train_code']].copy()

    # 필요한 데이터만 남기기 (이동 시간 계산 등)
    # 이동 시간 = 다음 역 도착 시간 - 현재 역 출발 시간
    valid_edges['travel_time'] = valid_edges['next_arr_sec'] - valid_edges['dept_sec']

    # 5. 요일별 그래프 생성 및 저장
    day_types = {
        'DAY': 'weekday',
        'SAT': 'saturday',
        'END': 'holiday' # END가 일요일/공휴일이라고 가정
    }

    # 출력 폴더 확인
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("그래프 생성 및 저장 중...")
    
    for raw_day, file_suffix in day_types.items():
        # 해당 요일 데이터만 필터링
        day_df = valid_edges[valid_edges['주중주말'] == raw_day]
        
        # 그래프 초기화
        graph = {}
        
        # DataFrame을 순회하며 그래프 구축 (이 부분은 GroupBy로 최적화)
        # 역별로 그룹핑하여 처리
        for station_code, group in day_df.groupby('역사코드'):
            if station_code not in graph:
                graph[station_code] = []
            
            # 해당 역에서 출발하는 모든 간선 정보 리스트로 변환
            for _, row in group.iterrows():
                edge = {
                    "dest_code": row['next_station_code'],  # 다음 역 코드
                    "dest_name": row['next_station_name'],  # 다음 역 이름 (UI용)
                    "line": row['호선'],
                    "train_code": row['열차코드'],
                    "dept_time": row['dept_sec'],          # 현재 역 출발 시각 (초)
                    "arr_time": row['next_arr_sec'],       # 다음 역 도착 시각 (초)
                    "travel_time": row['travel_time'],     # 이동 소요 시간 (초)
                    "express": row['급행여부']             # 1: 급행, 0: 완행
                }
                graph[station_code].append(edge)
        
        # 시간순 정렬 (이진 탐색 알고리즘 활용을 위해 필수)
        for station in graph:
            graph[station].sort(key=lambda x: x['dept_time'])

        # JSON 파일 저장
        output_file = f"{OUTPUT_DIR}graph_{file_suffix}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2) # indent는 디버깅용, 실제 서비스땐 제거 권장
        
        print(f" -> {output_file} 저장 완료 ({len(graph)}개 역)")

    # 6. 전체 역 목록(Station List) 별도 저장 (검색 자동완성용)
    unique_stations = df[['역사코드', '역사명', '호선']].drop_duplicates().to_dict(orient='records')
    with open(f"{OUTPUT_DIR}stations_list.json", 'w', encoding='utf-8') as f:
        json.dump(unique_stations, f, ensure_ascii=False)
    print(" -> stations_list.json 저장 완료")

if __name__ == "__main__":
    preprocess_timetable()