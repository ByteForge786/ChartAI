import re
from dateutil import parser
from dateutil.parser import ParserError

def parse_date_range(question):
    # Updated pattern to include more date formats
    date_pattern = r'\b(?:from|between)?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?|(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01]))(?:[,\s]+\d{4})?\s*(?:to|[-–—])\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?|(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01]))(?:[,\s]+\d{4})?\b'

    matches = re.findall(date_pattern, question, re.IGNORECASE)
    
    if not matches:
        return None, None, "No date range found in the question. Please provide a full date range in your question."

    start_date_str, end_date_str = matches[0]

    try:
        # Parse dates
        start_date = parser.parse(start_date_str, fuzzy=False)
        end_date = parser.parse(end_date_str, fuzzy=False)
    except ParserError:
        return None, None, "Unable to parse the dates. Please provide full dates including the year (e.g., 1 Jan 2024 to 3 Jan 2024)."

    # Check if year is present in the original strings
    if not (re.search(r'\d{4}', start_date_str) and re.search(r'\d{4}', end_date_str)):
        return None, None, "Please provide full dates including the year for both start and end dates."

    # Validate date range
    if start_date > end_date:
        return None, None, "Invalid date range. The start date should be before the end date."

    return start_date, end_date, "Date range found and parsed successfully."

def test_parse_date_range():
    test_cases = [
        ("What happened from 1 Jan 2024 to 3 Jan 2024?", True),
        ("Events between January 15, 2024 and January 20, 2024", True),
        ("Show me data from 1 June 2024 to 1 July 2024", True),
        ("Information from 5 May to 10 May", False),
        ("Data between 3/15 and 3/20", False),
        ("What occurred from 2024-03-01 to 2024-03-05?", True),
        ("Happenings from March 1st to April 1st", False),
        ("Events from 31 December 2024 to 1 January 2025", True),
        ("Data from 1 January 2025 to 31 December 2024", False),
        ("What happened yesterday?", False),
        ("Show me everything", False),
        ("Events from Jan 1 2024 to Jan 3 2024", True),
        ("Data between 1 Jan and 3 Jan", False),
    ]

    for question, should_pass in test_cases:
        start_date, end_date, message = parse_date_range(question)
        if should_pass:
            assert start_date and end_date, f"Failed to parse valid date range: {question}"
            print(f"Passed: {question}")
            print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
            print(f"End date: {end_date.strftime('%Y-%m-%d')}")
        else:
            assert not start_date and not end_date, f"Incorrectly parsed invalid date range: {question}"
            print(f"Correctly rejected: {question}")
            print(f"Message: {message}")
        print()

if __name__ == "__main__":
    test_parse_date_range()
