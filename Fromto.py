import re
from datetime import datetime

def parse_date(date_str):
    date_str = date_str.strip()
    
    # Remove ordinal suffixes
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    formats = [
        "%d %b %Y",     # 01 Jan 2024
        "%d %B %Y",     # 01 January 2024
        "%B %d %Y",     # January 01 2024
        "%b %d %Y",     # Jan 01 2024
        "%Y %b %d",     # 2024 Jan 01
        "%Y %B %d",     # 2024 January 01
        "%m/%d/%Y",     # 01/01/2024
        "%d/%m/%Y",     # 01/01/2024 (Day/Month format)
        "%Y-%m-%d",     # 2024-01-01
        "%Y/%m/%d",     # 2024/01/01
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    
    raise ValueError(f"Unable to parse date: {date_str}")

def parse_date_range(question):
    # Pattern to match various date formats
    pattern = r'(?:from|between)?\s*(\d{1,4}(?:(?:st|nd|rd|th)?\s+)?(?:[/\-\s])?(?:\w+|[/\-])?(?:[/\-\s])?\d{1,4}(?:(?:st|nd|rd|th)?\s+)?(?:[/\-\s])?(?:\w+|\d{1,4})?)\s*(?:to|and|[-–—])\s*(\d{1,4}(?:(?:st|nd|rd|th)?\s+)?(?:[/\-\s])?(?:\w+|[/\-])?(?:[/\-\s])?\d{1,4}(?:(?:st|nd|rd|th)?\s+)?(?:[/\-\s])?(?:\w+|\d{1,4})?)'
    
    match = re.search(pattern, question, re.IGNORECASE)
    
    if not match:
        return None, None, "No date range found in the question. Please provide a full date range in your question."

    start_date_str, end_date_str = match.groups()

    try:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    except ValueError as e:
        return None, None, str(e)

    # Validate date range
    if start_date > end_date:
        return None, None, "Invalid date range. The start date should be before the end date."

    return start_date, end_date, "Date range found and parsed successfully."

def test_parse_date_range():
    test_cases = [
        ("What happened from 1 Jan 2024 to 3 Jan 2024?", True),
        ("Events between 15 January 2024 and 20 January 2024", True),
        ("Show me data from 1 June 2024 to 1 July 2024", True),
        ("Information from 5 May to 10 May", False),
        ("Events from 31 December 2024 to 1 January 2025", True),
        ("Data from 1 January 2025 to 31 December 2024", False),
        ("Conference from 1st January 2024 to 5th January 2024", True),
        ("Meetings from 2024 Jan 01 to 2024 Jan 05", True),
        ("Seminar between 2024 February 15 and 2024 February 20", True),
        ("Project timeline from 01/15/2024 to 06/30/2024", True),
        ("Report period: 2024-03-01 to 2024-03-31", True),
        ("Analysis from 1/1/2024 to 12/31/2024", True),
        ("Data range: 2024/01/01 - 2024/12/31", True),
        ("Study conducted between 15-01-2024 and 30-06-2024", True),
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
