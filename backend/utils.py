class TimeUtils:
    @staticmethod
    def str_to_seconds(t_str):
        """ 문자열(HH:MM:SS) -> 초(int) 변환 """
        if t_str is None or t_str != t_str:  # t_str != t_str 은 NaN을 체크하는 방법
            return None

        try:
            parts = list(map(int, str(t_str).split(':')))       # HH:MM:SS 또는 MM:SS 형태로 정수 list 생성 (길이는 알아서)
            if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2: return parts[0] * 60 + parts[1]
            return 0
        except:
            return 0

    @staticmethod
    def seconds_to_str(seconds):
        """ 초(int) -> 문자열(HH:MM:SS) 변환 """
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}"