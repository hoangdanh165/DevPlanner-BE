def record_ai_usage(model_name, token_usage, cost_per_1k=0.0005):
    input_tokens = token_usage.get("input_tokens", 0)
    output_tokens = token_usage.get("output_tokens", 0)
    total = (input_tokens + output_tokens) / 1000 * cost_per_1k
    return round(total, 6)
