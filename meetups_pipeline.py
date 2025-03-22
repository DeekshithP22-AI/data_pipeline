from crawl4ai import AsyncWebCrawler
import asyncio
import json
from datetime import datetime

async def scrape_startup_events():
    try:
        async with AsyncWebCrawler(
            # Basic configuration
            browser_type="chromium",
            headless=False,
            verbose=True,
            
            # Anti-detection settings
            simulate_user=True,
            magic=True,
            
            # Browser settings
            page_timeout=120000
        ) as crawler:
            # First handle the login
            print("Navigating to login page...")
            await crawler.arun(
                url="https://www.meetup.com/login",
                delay_before_return_html=3.0
            )

            print("Looking for Google login button...")
            await crawler.arun(
                url="https://www.meetup.com/login",
                js_code=[
                    """
                    function findGoogleLogin() {
                        const buttons = Array.from(document.querySelectorAll('button, a'));
                        const googleButton = buttons.find(button => 
                            button.textContent.toLowerCase().includes('google') || 
                            button.innerHTML.toLowerCase().includes('google')
                        );
                        if (googleButton) {
                            console.log('Found Google button:', googleButton.textContent);
                            googleButton.click();
                            return true;
                        }
                        return false;
                    }
                    findGoogleLogin();
                    """
                ],
                delay_before_return_html=3.0
            )

            print("\nPlease complete Google login in the browser window...")
            print("The script will wait 45 seconds for you to login...")
            await asyncio.sleep(45)
            
            print("\nVerifying login status...")
            verify_result = await crawler.arun(
                url="https://www.meetup.com/",
                js_code=[
                    """
                    console.log('Current URL:', window.location.href);
                    const isLoggedIn = !document.querySelector('a[href*="login"]');
                    console.log('Login status:', isLoggedIn);
                    return isLoggedIn;
                    """
                ]
            )

            print("Proceeding to startup events page...")
            # Extract events using JavaScript
            result = await crawler.arun(
                url="https://www.meetup.com/find/?keywords=startup",
                js_code=[
                    """
                    async function extractEvents() {
                        // First scroll to load more content
                        for(let i = 0; i < 3; i++) {
                            window.scrollTo(0, document.body.scrollHeight);
                            await new Promise(r => setTimeout(r, 1500));
                            console.log('Scroll attempt:', i + 1);
                        }
                        
                        // Find all event containers
                        const events = [];
                        const eventContainers = document.querySelectorAll('div.px-5.w-full.bg-white.border-b, article');
                        console.log('Found containers:', eventContainers.length);
                        
                        eventContainers.forEach((container, index) => {
                            // Extract event details
                            const title = container.querySelector('h1, h2, h3')?.textContent?.trim();
                            const description = container.querySelector('p:not([class*="location"])')?.textContent?.trim();
                            const location = container.querySelector('[class*="location"]')?.textContent?.trim();
                            const dateElement = container.querySelector('time, [class*="date"]');
                            const dateText = dateElement?.textContent?.trim();
                            const dateAttr = dateElement?.getAttribute('datetime');
                            
                            // Find the event link
                            const linkElement = container.querySelector('a[href*="/events/"]');
                            const url = linkElement?.href;
                            
                            console.log(`Processing event ${index + 1}:`, title);
                            
                            if (title || url) {
                                events.push({
                                    title: title || 'No title',
                                    description: description || '',
                                    location: location || '',
                                    date: dateText || '',
                                    datetime: dateAttr || '',
                                    url: url || ''
                                });
                            }
                        });
                        
                        console.log(`Found ${events.length} events`);
                        return events;
                    }
                    extractEvents();
                    """
                ],
                delay_before_return_html=10.0
            )

            # Process events from JavaScript result
            events = []
            if hasattr(result, 'js_result') and result.js_result:
                events = result.js_result
                print(f"\nFound {len(events)} events in JavaScript result")
            
            # Clean up the events data
            valid_events = []
            for event in events:
                if isinstance(event, dict) and (event.get('url') or event.get('title')):
                    # Clean the data
                    cleaned_event = {}
                    for key, value in event.items():
                        if isinstance(value, str):
                            cleaned_value = value.strip()
                            if key == 'url' and not cleaned_value.startswith('http'):
                                cleaned_value = 'https://www.meetup.com' + cleaned_value
                            cleaned_event[key] = cleaned_value
                    valid_events.append(cleaned_event)

            print(f"After cleaning: {len(valid_events)} valid events")
            return valid_events

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        return []

async def main():
    events = await scrape_startup_events()
    
    if events:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"startup_events_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"\nEvents saved to {filename}")
        
        print("\nSample of scraped events:")
        for event in events[:3]:
            print(f"\nTitle: {event.get('title', 'No title')}")
            print(f"URL: {event.get('url', 'No URL')}")
            print(f"Location: {event.get('location', 'No location')}")
            print(f"Date: {event.get('date', 'No date')}")
            if event.get('description'):
                print(f"Description: {event['description'][:100]}...")
            print("-" * 50)
    else:
        print("\nNo events were scraped. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
    

