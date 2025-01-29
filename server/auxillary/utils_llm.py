import ollama

def segment_and_summarize(sentences : list[dict]):
    prompt = f"""
    You are given a transcript of a video. Your tasks:
    1. Provide a brief sentence summary for each segment.

    (Similiar to how YouTube videos are sectioned based on context)

    Sentences metadata (extracted from transcript of the video itself):
    {sentences}

    Provide output in this format:
    Segment 1 (0s - 12s): Summary of the first segment.
    Segment 2 (12s - 20s): Summary of the second segment.
    and so on.

    Make sure every sentence is included, and thar you do not leave out anything. No comments of your own, only output in the specified format
    """

    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]