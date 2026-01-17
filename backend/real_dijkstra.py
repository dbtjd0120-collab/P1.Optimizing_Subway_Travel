import os
import json
import heapq
from datetime import datetime

# --- 경로 설정 ---
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(current_file)
project_root = os.path.dirname(backend_dir)
DATA_DIR = os.path.join(project_root, 'data', 'processed')

class SubwayPathfinder:
    def __init__(self):
        """
        함수 정의 앞에 붙은 _ 두개는 name mangling(이름변경). 규칙에 따라 외부에서 접근 불가
        같은 클래스의 다른 함수를 사용할 것이라 self를 인자로 정의함
        """
        self.day_type = self._get_today_type()
        self._load_data()
    
        # print(f"[{self.day_type}] 데이터 로딩 완료. 탐색 준비가 되었습니다.")

    def _get_today_type(self):  # 날짜를 요일로   + 한국의 현재 시간을 불러오는 datetime.now().time()도 고려 해볼만함.
        """함수 정의 앞에 붙은 _ 하나는 내부용(private) 메서드임을 나타냄"""
    
        day_type = datetime.now().weekday() #오늘이 무슨 요일인지 월:0 - 일:6으로 표현
        if day_type < 5: 
            return 'weekday'
        elif day_type == 5: 
            return 'saturday'
        else: 
            return 'holiday'
        

    def _load_data(self):
        try:
            # --- 요일별 운행 그래프 파일 선택 ---
            if self.day_type == 'weekday':
                graph_file = 'graph_weekday.json'
            elif self.day_type == 'saturday':
                graph_file = 'graph_saturday.json'
            else:  # holiday
                graph_file = 'graph_holiday.json'

            # --- 열차 운행 그래프 로드 ---
            with open(os.path.join(DATA_DIR, graph_file), 'r', encoding='EUC-KR') as f:
                self.graph = json.load(f)

            # --- 환승 정보 로드 ---
            with open(os.path.join(DATA_DIR, 'transfer_list.json'), 'r', encoding='EUC-KR') as f:
                self.transfers = json.load(f)

            # --- 역 메타 정보 로드 ---
            with open(os.path.join(DATA_DIR, 'stations_list.json'), 'r', encoding='EUC-KR') as f:
                self.stations_raw = json.load(f)

        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            exit()





    def _get_start_states(self, start_station_name: str):
        """
        사용자가 입력한 출발역(역사명)을 기준으로
        역사코드 / 호선 / 급행 가능 여부를 반환
        """

        start_states = []

        for station in self.stations_raw:
            # ✅ 실제 필드명 사용
            if station["역사명"] != start_station_name:
                continue

            station_code = station["역사코드"]
            line = station["호선"]

            has_express = False

            # 이 역사코드에서 출발하는 열차가 있는지 확인
            if station_code in self.graph:
                for edge in self.graph[station_code]:
                    if edge.get("express", 0) == 1:
                        has_express = True
                        break

            start_states.append({
                "역사명": start_station_name,
                "역사코드": station_code,
                "호선": line,
                "급행가능": has_express
            })

        if not start_states:
            raise ValueError(f"출발역 '{start_station_name}' 을(를) 찾을 수 없습니다.")

        return start_states



    def find_path(self, start_station_name):
        start_states = self._get_start_states(start_station_name)

        heap = []
        dist = {}

        start_time = (
            datetime.now().hour * 3600 +
            datetime.now().minute * 60 +
            datetime.now().second
        )

        # 시작 노드 삽입
        for state in start_states:
            station_code = state["역사코드"]
            line = state["호선"]

            if state["급행가능"]:
                for is_express in (False, True):
                    node = (station_code, line, is_express)
                    dist[node] = 0
                    heapq.heappush(heap, (0, node))
            else:
                node = (station_code, line, False)
                dist[node] = 0
                heapq.heappush(heap, (0, node))

        # ✅ 다익스트라 루프
        while heap:
            current_cost, (station_code, line, is_express) = heapq.heappop(heap)
            current_time = start_time + current_cost

            if current_cost > dist[(station_code, line, is_express)]:
                continue

            for edge in self.graph.get(station_code, []):

                if edge["dept_time"] < current_time:
                    continue

                if is_express and edge["express"] == 0:
                    continue
                if not is_express and edge["express"] == 1:
                    continue

                wait_time = edge["dept_time"] - current_time
                travel_time = edge["arr_time"] - edge["dept_time"]
                next_cost = current_cost + wait_time + travel_time

                next_node = (
                    edge["dest_code"],
                    edge["line"],
                    is_express
                )

                if next_node not in dist or next_cost < dist[next_node]:
                    dist[next_node] = next_cost
                    heapq.heappush(heap, (next_cost, next_node))


        



            

