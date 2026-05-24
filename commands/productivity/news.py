import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
from datetime import datetime

def news_headlines(lang="en"):
    """
    Fetches the latest top news headlines from BBC News.
    
    :param lang: Language for the news (default: English)
                 Supported: en (English), etc.
    :return: Formatted string of news headlines or error message
    """
    # Using BBC News as a reliable, non-API source for top headlines
    url = "https://www.bbc.com/news"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Download the page content
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status() # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract top headlines
        # BBC structure uses data-testid="card-headline" or h2 for main headlines
        headlines = soup.find_all(attrs={"data-testid": "card-headline"})
        if not headlines:
            headlines = soup.find_all('h2')
        if not headlines:
            headlines = soup.find_all('h3')
            
        if not headlines:
            return "Could not find any headlines. The website structure may have changed."
        
        # Clean and format the headlines
        news_list = []
        for i, headline in enumerate(headlines[:5], 1): # Get top 5
            title = headline.get_text(strip=True)
            if title and len(title) > 10: # Filter out short or empty titles
                news_list.append(f"{i}. {title}")
        
        if not news_list:
            return "Found headlines but couldn't extract readable titles."
        
        # Get current time for context
        current_time = datetime.now().strftime("%H:%M")
        
        # Format the final output
        output = f"Here are the top {len(news_list)} headlines as of {current_time}:\n\n"
        output += "\n".join(news_list)
        
        return output
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching news: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
