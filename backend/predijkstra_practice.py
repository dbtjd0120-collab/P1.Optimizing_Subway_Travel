graph = {
    # 1호선 일반
    "A": {"B": 2},
    "B": {"A": 2, "C": 2, "D": 3},   # B → D 급행 (3분)
    "C": {"B": 2, "D": 2},
    "D": {"C": 2, "E": 2, "B": 3, "H": 2, "I": 2},
    "E": {"D": 2, "F": 2},
    "F": {"E": 2},

    # 2호선 일반
    "G": {"H": 2},
    "H": {"G": 2, "D": 2},
    "I": {"D": 2, "J": 2},
    "J": {"I": 2},
}


import heapq


def dijkstra(graph, start, end):
    pq = []
    heapq.heappush(pq, (0, start))

    dist = {start: 0}
    prev = {}

    while pq:
        curr_dist, curr = heapq.heappop(pq)

        if curr_dist > dist.get(curr, float("inf")):
            continue

        if curr == end:
            break

        for nxt, weight in graph.get(curr, {}).items():
            new_dist = curr_dist + weight

            if new_dist < dist.get(nxt, float("inf")):
                dist[nxt] = new_dist
                prev[nxt] = curr
                heapq.heappush(pq, (new_dist, nxt))

    if end not in dist:
        return None, None

    # 경로 복원
    path = []
    node = end
    while node != start:
        path.append(node)
        node = prev[node]
    path.append(start)
    path.reverse()

    return path, dist[end]

def run():
    start_station = input("출발역을 입력하세요: ").strip()
    end_station = input("도착역을 입력하세요: ").strip()

    if start_station not in graph or end_station not in graph:
        print("존재하지 않는 역입니다.")
        return

    path, total_time = dijkstra(graph, start_station, end_station)

    if path is None:
        print("경로를 찾을 수 없습니다.")
        return

    print("\n🚇 최단 시간 경로")
    print(" → ".join(path))
    print(f"총 소요 시간: {total_time}분")

if __name__ == "__main__":
    run()

