import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
import re
import random
from fake_useragent import UserAgent
import urllib.parse

class BingScholarFinder:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        user_agent = self.ua.random
        options.add_argument(f'--user-agent={user_agent}')
        print(f"🔧 Setting up undetected Chrome driver...")
        print(f"📱 User Agent: {user_agent}")
        print(f"🖥️  Window size: {width}x{height}")
        try:
            self.driver = uc.Chrome(options=options, version_main=129, use_subprocess=True)
            print("✅ Driver setup complete!")
            return True
        except Exception as e:
            print(f"❌ Failed to setup driver: {e}")
            return False
    
    def search_bing_for_scholar(self, name, institution="UC Berkeley"):
        try:
            query = f'{name} berkeley google scholar'
            print(f"🔍 Searching Bing for: {name}")
            self.driver.get("https://www.bing.com/")
            time.sleep(random.uniform(2, 4))
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(3, 6))
            
            # Look for all links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            # Search for Google Scholar profile links
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        # Check if it's a Bing redirect URL containing Google Scholar
                        if 'bing.com/ck/' in href and 'scholar.google.com' in href:
                            # Extract the actual URL from the Bing redirect
                            # Parse the URL to get the 'u' parameter
                            parsed = urllib.parse.urlparse(href)
                            query_params = urllib.parse.parse_qs(parsed.query)
                            if 'u' in query_params:
                                actual_url = urllib.parse.unquote(query_params['u'][0])
                                if 'scholar.google.com/citations?user=' in actual_url:
                                    match = re.search(r'user=([^&]+)', actual_url)
                                    if match:
                                        scholar_id = match.group(1)
                                        print(f"✅ Found profile: {actual_url}")
                                        print(f"🆔 Scholar ID: {scholar_id}")
                                        return {
                                            "scholar_id": scholar_id,
                                            "profile_url": actual_url
                                        }
                        
                        # Also check for direct Google Scholar links
                        elif 'scholar.google.com/citations?user=' in href:
                            match = re.search(r'user=([^&]+)', href)
                            if match:
                                scholar_id = match.group(1)
                                print(f"✅ Found profile: {href}")
                                print(f"🆔 Scholar ID: {scholar_id}")
                                return {
                                    "scholar_id": scholar_id,
                                    "profile_url": href
                                }
                except Exception as e:
                    continue
            
            print(f"❌ No Scholar profile found for {name}")
            return None
        except Exception as e:
            print(f"❌ Error searching Bing for {name}: {e}")
            return None
    
    def close(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Driver closed")

def main():
    print("🔍 Bing Scholar Profile Finder (undetected-chromedriver)")
    print("=" * 60)
    try:
        with open("faculty_professors.json", "r") as f:
            professors = json.load(f)
        print(f"📚 Loaded {len(professors)} professors")
    except FileNotFoundError:
        print("❌ faculty_professors.json not found!")
        return
    results_file = "bing_scholar_results.json"
    existing_results = {}
    try:
        with open(results_file, "r") as f:
            existing_results = json.load(f)
        print(f"📝 Loaded {len(existing_results)} existing results")
    except FileNotFoundError:
        pass
    finder = BingScholarFinder(headless=False)
    if not finder.setup_driver():
        print("❌ Failed to setup driver!")
        return
    enriched_professors = []
    try:
        for i, prof in enumerate(professors):
            name = prof['name']
            if name in existing_results:
                print(f"⏭️  Skipping {name} (already processed)")
                enriched_prof = {**prof, **existing_results[name]}
                enriched_professors.append(enriched_prof)
                continue
            print(f"\n--- Processing {i+1}/{len(professors)}: {name} ---")
            profile_info = finder.search_bing_for_scholar(name)
            if profile_info:
                existing_results[name] = {
                    "google_scholar_id": profile_info["scholar_id"],
                    "scholar_profile_url": profile_info["profile_url"]
                }
                enriched_prof = {**prof, **existing_results[name]}
                enriched_professors.append(enriched_prof)
                print(f"✅ Found Scholar profile for: {name}")
            else:
                enriched_professors.append(prof)
                print(f"⚠️  No Scholar profile found for {name}")
            with open(results_file, "w") as f:
                json.dump(existing_results, f, indent=2)
            time.sleep(random.uniform(5, 10))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        finder.close()
    output_file = "enriched_professors_data.json"
    with open(output_file, "w") as f:
        json.dump(enriched_professors, f, indent=2)
    print(f"\n🎉 Processing complete!")
    print(f"📊 Processed: {len(professors)} professors")
    print(f"✅ Found Scholar profiles: {len([p for p in enriched_professors if 'google_scholar_id' in p])} professors")
    print(f"💾 Saved to: {output_file}")
    print(f"📝 Intermediate results: {results_file}")

if __name__ == "__main__":
    main() 