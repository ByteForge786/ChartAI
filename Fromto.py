import re
from datetime import datetime

def find_date_range_in_question(question):
    # Patterns to match various date formats
    date_patterns = [
        r'\b(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{2,4})\b',  # DD/MM/YYYY or similar
        r'\b(\d{1,2})(?:st|nd|rd|th)?[ ]*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{4})?\b',  # 3rd March 2024 or 3 March
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{1,2})(?:st|nd|rd|th)?[ ]*(\d{4})?\b',  # March 3rd, 2024 or March 3
    ]
    
    # Combined regex to match date ranges in the form 'from date to date'
    range_pattern = re.compile(
        r'from\s+(' + '|'.join(date_patterns) + r')\s+to\s+(' + '|'.join(date_patterns) + r')',
        re.IGNORECASE
    )

    matches = range_pattern.findall(question)
    
    if matches:
        for match in matches:
            start_date = ' '.join([group for group in match[:3] if group])
            end_date = ' '.join([group for group in match[3:] if group])
            
            # Checking if both dates are fully specified
            if re.match(r'\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{2,4}', start_date) and re.match(r'\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{2,4}', end_date):
                print(f"Valid date range found: from {start_date} to {end_date}")
                return True
            elif any(re.search(r'\d{4}', date) is None for date in [start_date, end_date]):
                print("Please write the full date you want, including the year.")
                return False
        return True
    else:
        print("No valid date range found.")
        return False

# Test the utility
questions = [
    "Can you schedule a meeting from 3 March to 4 March 2024?",
    "Please book the venue from 06/07/2024 to 10/07/2024.",
    "I need the report from March 3 to March 4.",
    "Plan the event from June 15 to 20, 2024.",
    "Reserve the conference room from 5 July to 6 July.",
    "What are the available dates from 07/15 to 07/18?",
]

for q in questions:
    print(f"Question: '{q}'")
    find_date_range_in_question(q)
    print()
