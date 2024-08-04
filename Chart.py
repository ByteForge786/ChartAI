import re

def get_chart_type(sentence):
    keywords = ['bar', 'grouped bar', 'line', 'scatter', 'histogram', 'pie']
    
    # Convert the input sentence to lowercase
    sentence_lower = sentence.lower()
    
    # Create regex patterns for each keyword
    patterns = [
        r'\b' + re.escape(keyword.replace(' ', r'\s*')) + r'\b'
        for keyword in keywords
    ]
    
    # Search for each pattern in the lowercase sentence
    for keyword, pattern in zip(keywords, patterns):
        if re.search(pattern, sentence_lower):
            return keyword
    
    return None  # Return None if no keyword matches

# Example usage
sentences = [
    "I think a Bar chart would be good for this data.",
    "A Grouped    Bar chart might show the comparison better.",
    "Let's use a line graph to show the trend.",
    "A pie chart isn't suitable for this dataset.",
    "We should visualize this with a histogram.",
    "This data doesn't fit any of our chart types.",
    "A scatter plot would work well here.",
    "Maybe a GROUPED-BAR chart?",
    "How about a BAR-CHART?",
    "A Line-Graph could show the trend."
]

for sentence in sentences:
    print(f"Sentence: {sentence}")
    print(f"Chart type: {get_chart_type(sentence)}\n")
