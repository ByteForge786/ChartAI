import re

def contains_date_range(question):
    # Patterns to match various date formats
    date_patterns = [
        r'\b(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{2,4})\b',  # DD/MM/YYYY or similar
        r'\b(\d{1,2})(?:st|nd|rd|th)?[ ]*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{4})?\b',  # 3rd March 2024 or 3 March
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{1,2})(?:st|nd|rd|th)?[ ]*(\d{4})?\b',  # March 3rd, 2024 or March 3
        r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b',  # YYYY-MM-DD or YYYY/MM/DD
        r'\b(\d{4})(\d{2})(\d{2})\b',  # YYYYMMDD or similar
        r'\b(\d{2})(\d{2})(\d{4})\b',  # DDMMYYYY or similar
    ]

    # Regex to match 'from date to date' or 'between date and date'
    range_pattern = re.compile(
        r'(from|between)\s+(' + '|'.join(date_patterns) + r')\s+(to|and)\s+(' + '|'.join(date_patterns) + r')',
        re.IGNORECASE
    )

    if range_pattern.search(question):
        return True
    else:
        return False

# Test the utility
questions = [
    "Can you schedule a meeting from 3 March to 4 March 2024?",
    "Please book the venue between 06/07/2024 and 10/07/2024.",
    "I need the report from March 3 to March 4.",
    "What are the available dates between 2024-08-15 and 2024-08-18?",
    "We have meetings from 15082024 to 18082024.",
    "Arrange the interview from June 15 to June 20, 2024.",
    "Check availability between 15th July 2024 and 20th July 2024.",
    "Is there any event between 20231205 and 20231208?",
    "Let's block dates from 06-12-2024 to 10-12-2024.",
    "Can you find the slot between 05122023 and 08122023?",
    "Does this include dates from 3rd March to 4th March?",
    "Is there anything between April 1 and April 2?",
]

for q in questions:
    print(f"Question: '{q}' -> Contains date range: {contains_date_range(q)}")



import re

import re

import re

def contains_date_range(question):
    # Patterns to match various date formats
    date_patterns = [
        r'\b(\d{1,2})(?:st|nd|rd|th)?\s*[\/\.\-\s]\s*(\d{1,2})(?:st|nd|rd|th)?\s*[\/\.\-\s]\s*(\d{2,4})\b',  # DD/MM/YYYY or similar
        r'\b(\d{1,2})(?:st|nd|rd|th)?\s*(?:of)?\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*(?:,?\s*(\d{4}))?\b',  # 3rd March 2024 or 3 March
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*(\d{1,2})(?:st|nd|rd|th)?\s*(?:,?\s*(\d{4}))?\b',  # March 3rd, 2024 or March 3
        r'\b(\d{4})[\/\.\-\s](\d{1,2})[\/\.\-\s](\d{1,2})\b',  # YYYY-MM-DD or YYYY/MM/DD
        r'\b(\d{4})(\d{2})(\d{2})\b',  # YYYYMMDD or similar
        r'\b(\d{2})(\d{2})(\d{4})\b',  # DDMMYYYY or similar
    ]
    
    # Join the patterns with more flexible spacing
    date_pattern = '|'.join(f'(?:{pattern})' for pattern in date_patterns)
    
    # Regex to match 'from date to date' or 'between date and date' with very flexible spacing
    range_pattern = re.compile(
        r'(from|between)\s*(' + date_pattern + r')\s*(?:to|and|-)\s*(' + date_pattern + r')',
        re.IGNORECASE | re.VERBOSE
    )
    
    if range_pattern.search(question):
        return True
    else:
        return False

# Test the utility
questions = [
    "Can you schedule a meeting from 3 March to 4 March 2024?",
    "Please book the venue between 06/07/2024 and 10/07/2024.",
    "I need the report from March 3 to March 4.",
    "What are the available dates between 2024-08-15 and 2024-08-18?",
    "We have meetings from 15082024 to 18082024.",
    "Arrange the interview from June 15 to June 20, 2024.",
    "Check availability between 15th July 2024 and 20th July 2024.",
    "Is there any event between 20231205 and 20231208?",
    "Let's block dates from 06-12-2024 to 10-12-2024.",
    "Can you find the slot between 05122023 and 08122023?",
    "Does this include dates from 3rd March to 4th March?",
    "Is there anything between April 1 and April 2?",
    "Can you schedule a meeting from   3 March    to     4 March 2024?",  # Extra spaces
    "Please book the venue between 06/07/2024    and    10/07/2024.",     # Extra spaces
    "Let's block dates from 06-12-2024  -  10-12-2024.",                  # Dash separator with spaces
    "From 4th June to 5 th June 2024",                                    # Spaces in ordinal
    "Between the 1st of May and the 3rd of June",                         # 'of' in date
    "From 2023.06.01 to 2023.06.30",                                      # Dot as separator
    "Between 1 Jan and 31 Dec 2024",                                      # Short month names without year in first date
]

for q in questions:
    print(f"Question: '{q}' -> Contains date range: {contains_date_range(q)}")
