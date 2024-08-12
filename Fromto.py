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



import re
from datetime import datetime

def find_date_range_in_question(question):
    # Patterns to match various date formats
    date_patterns = [
        r'\b(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{2,4})\b',  # DD/MM/YYYY or similar
        r'\b(\d{1,2})(?:st|nd|rd|th)?[ ]*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{4})?\b',  # 3rd March 2024 or 3 March
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ]*(\d{1,2})(?:st|nd|rd|th)?[ ]*(\d{4})?\b',  # March 3rd, 2024 or March 3
        r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b',  # YYYY-MM-DD or YYYY/MM/DD
        r'\b(\d{4})(\d{2})(\d{2})\b',  # YYYYMMDD or similar
        r'\b(\d{2})(\d{2})(\d{4})\b',  # DDMMYYYY or similar
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

# Test the utility with various formats
questions = [
    "Can you schedule a meeting from 3 March to 4 March 2024?",
    "Please book the venue from 06/07/2024 to 10/07/2024.",
    "I need the report from March 3 to March 4.",
    "Plan the event from June 15 to 20, 2024.",
    "Reserve the conference room from 5 July to 6 July.",
    "What are the available dates from 07/15 to 07/18?",
    "Set up the call from 2024-03-03 to 2024-03-04.",
    "The workshop is scheduled from 20240815 to 20240818.",
    "We have meetings from 15082024 to 18082024.",
    "Arrange the interview from 2024-08-15 to 2024-08-18.",
    "Can we confirm dates from 15th July 2024 to 20th July 2024?",
    "Check availability from 3rd May 24 to 4th May 24.",
    "Let's block dates from 06-12-2024 to 10-12-2024.",
    "Mark the calendar from 20231205 to 20231208.",
    "Can you find the slot from 05122023 to 08122023?",
]

for q in questions:
    print(f"Question: '{q}'")
    find_date_range_in_question(q)
    print()
