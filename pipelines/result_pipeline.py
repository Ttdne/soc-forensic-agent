def postprocess_result(result):
    if result is None:
        print("Warning: result is None.")
        return "Final Output: No result"
    print(f"Debug: result is {result}")
    return f"Final Output: {result.get('output', 'No result')}"
