from pathlib import Path


def calculate_model_configs(model_name: str) -> tuple[int, int]:

    default_max_retries = 3
    default_retry_duration = 2

    rate_limit_path = Path("rate_limits.txt")

    if not rate_limit_path.exists():
        return default_max_retries, default_retry_duration

    with open(rate_limit_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("<MODEL_NAME") or not line.strip():
                continue

            parts = line.split()
            if parts and parts[0] == model_name:
                try:
                    rpm = int(parts[1])
                    # 60s/5rpm = 12s intervals; 60s/10rpm = 6s intervals
                    calculated_duration = max(1, 60 // rpm)
                    max_retries = min(5, rpm)
                    return max_retries, calculated_duration
                except ValueError, IndexError:
                    break

    return default_max_retries, default_retry_duration
