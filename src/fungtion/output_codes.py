def format_output_code(index, total_count, minimum_width=4):
    """Return a zero-padded output code that expands for large runs."""
    width = max(minimum_width, len(str(total_count)))
    return f"{index:0{width}d}"
