import heapq

"""
           -(3분, 급행)-  [I]—2분—[J]
          /            \ /
[A]—2분—[B]—2분—[C]—2분—[D]—2분—[E]—2분—[F]
                       /
             [G]—2분—[H]
"""
                                 
graph = {
    "A":[{"to":"B","travel_time":2,"is_express":"False","line":"1호선"}],
    "B":[{"to":"A","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"C","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"D1","travel_time":3,"is_express":"True","line":"1호선"}],
    "C":[{"to":"B","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"D1","travel_time":2,"is_express":"False","line":"1호선"}],
    "D1":[{"to":"C","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"B","travel_time":3,"is_express":"True","line":"1호선"},
         {"to":"E","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"D2","travel_time":1,"is_express":"False","line":"ex"}],
    "D2":[{"to":"H","travel_time":2,"is_express":"False","line":"2호선"},
         {"to":"I","travel_time":2,"is_express":"False","line":"2호선"},
         {"to":"D1","travel_time":1,"is_express":"False","line":"ex"}],
    "E":[{"to":"D1","travel_time":2,"is_express":"False","line":"1호선"},
         {"to":"F","travel_time":2,"is_express":"False","line":"1호선"}],
    "F":[{"to":"E","travel_time":2,"is_express":"False","line":"1호선"}],
    "G":[{"to":"H","travel_time":2,"is_express":"False","line":"2호선"}],
    "H":[{"to":"D2","travel_time":2,"is_express":"False","line":"2호선"},
         {"to":"G","travel_time":2,"is_express":"False","line":"2호선"}],
    "I":[{"to":"D2","travel_time":2,"is_express":"False","line":"2호선"},
         {"to":"J","travel_time":2,"is_express":"False","line":"2호선"}],
    "J":[{"to":"I","travel_time":2,"is_express":"False","line":"2호선"}],
}


def djikstra(start):
    dist = {node:float('inf') for node in graph}
    dist[start] = 0
    pq = []
    heapq.heappush(pq, (0, start))
    path_log = {}

    while pq:
        cur_dist, cur_node = heapq.heappop(pq)

        if cur_dist > dist[cur_node]: continue

        for edge in graph[cur_node]:
            next_node = edge['to']
            cost = edge['travel_time']
            new_dist = cur_dist + cost

            if new_dist < dist[next_node]:
                path_log[next_node] = cur_node
                dist[next_node] = new_dist
                heapq.heappush(pq,(new_dist,next_node))
                """다음역:출발역, 다다음역:다음역"""

    return dist,path_log

def path_organizing(path_log, start, end):
    path = []
    while end != start:
        path.append(end)
        end = path_log[end]
    path.append(start)
    path.reverse()
    return path

if __name__ == "__main__":
    print("\n--- 🚉 지하철 길찾기 테스트 ---")
    start = input("출발역 입력 (예: 수유): ").strip()
    end = input("도착역 입력 (예: 강남): ").strip()
    # time_input = input("출발 시간 (HH:MM): ").strip()
    
    dist, path_log = djikstra(start)
    path = path_organizing(path_log, start, end)
    
    print(f"소요시간: {dist[end]}")
    print("경로: ", " -> ".join(path))