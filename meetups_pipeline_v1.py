import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://www.meetup.com/the-startup-club/events/304721346/?recId=0f5141c0-2d13-4864-adf2-547c44c476cb&recSource=keyword_search&searchId=c3b2a493-51fd-439a-b77b-639fcf96d825&eventOrigin=find_page$all")

        # Print the extracted content
        print(result.markdown)

# Run the async main function
asyncio.run(main())

