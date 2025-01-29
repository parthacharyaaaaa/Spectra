import ollama

def segment_and_summarize(transcript : str, sentences : list[dict]):
    prompt = f"""
    You are given a transcript of a video. Your tasks:
    1. Split the transcript into meaningful segments, ensuring each is no longer than 15 seconds.
    2. Provide a brief 1-2 sentence summary for each segment.
    3. Maintain the timestamp range for each segment.

    (Similiar to how YouTube videos are sectioned based on context)

    Full transcript as context:
    {transcript}

    Sentences metadata:
    {sentences}

    Provide output in this format:
    Segment 1 (0s - 12s): Summary of the first segment.
    Segment 2 (12s - 20s): Summary of the second segment.
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]