from bs4 import BeautifulSoup
import json
import glob
import os

def extract_professors_from_html(html_file):
    """
    Extract professor names and interests from a faculty page HTML file.
    Returns a list of dictionaries with 'name' and 'interests' keys.
    """
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all professor articles
    professor_articles = soup.find_all('article', class_='node--type-faculty')
    
    professors = []
    
    for article in professor_articles:
        # Extract name
        name_element = article.find('span', class_='field--name-title')
        if name_element:
            name = name_element.text.strip()
        else:
            continue  # Skip if no name found
        
        # Extract interests
        interests_element = article.find('div', class_='field--name-field-areas-of-expertise')
        interests = []
        
        if interests_element:
            # Find all interest links
            interest_links = interests_element.find_all('a')
            for link in interest_links:
                interest = link.text.strip()
                if interest:  # Only add non-empty interests
                    interests.append(interest)
        
        # Create professor entry
        professor = {
            'name': name,
            'interests': interests
        }
        
        professors.append(professor)
    
    return professors

def process_all_faculty_pages():
    """
    Process all faculty_page HTML files and extract professors.
    """
    # Find all faculty page HTML files
    faculty_files = glob.glob('faculty_page_*.html')
    faculty_files.sort()  # Sort to process in order
    
    if not faculty_files:
        print("No faculty_page HTML files found!")
        return
    
    print(f"Found {len(faculty_files)} faculty page files: {faculty_files}")
    
    all_professors = []
    total_new = 0
    
    # Process each faculty page
    for faculty_file in faculty_files:
        print(f"Processing {faculty_file}...")
        
        # Extract professors from the file
        professors = extract_professors_from_html(faculty_file)
        print(f"Found {len(professors)} professors in {faculty_file}")
        
        # Create a set of existing professor names for quick lookup
        existing_names = {prof['name'].lower() for prof in all_professors}
        
        # Filter out duplicates (based on name)
        unique_professors = []
        duplicates = 0
        
        for prof in professors:
            if prof['name'].lower() not in existing_names:
                unique_professors.append(prof)
            else:
                duplicates += 1
        
        if duplicates > 0:
            print(f"Skipped {duplicates} duplicate professors")
        
        # Add unique professors to the main list
        all_professors.extend(unique_professors)
        total_new += len(unique_professors)
    
    return all_professors, total_new

def save_professors_to_json(professors, output_file):
    """
    Save professors data to a JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(professors)} professors to {output_file}")

def print_summary(professors):
    """
    Print a summary of the extracted data.
    """
    print(f"\n=== SUMMARY ===")
    print(f"Total professors: {len(professors)}")
    
    # Count total interests
    total_interests = sum(len(prof['interests']) for prof in professors)
    print(f"Total interests: {total_interests}")
    
    # Show first few professors as example
    print(f"\n=== FIRST 5 PROFESSORS ===")
    for i, professor in enumerate(professors[:5]):
        print(f"{i+1}. {professor['name']}")
        print(f"   Interests: {', '.join(professor['interests'])}")
        print()

def main():
    # Process all faculty pages
    print("Extracting professors from faculty page HTML files...")
    all_professors, total_new = process_all_faculty_pages()
    
    if not all_professors:
        print("No professors found in the HTML files!")
        return
    
    # Save to JSON file
    save_professors_to_json(all_professors, 'faculty_professors.json')
    
    # Print summary
    print_summary(all_professors)
    
    print("\n=== EXTRACTION COMPLETE ===")
    print(f"Total unique professors: {len(all_professors)}")
    print(f"File created: faculty_professors.json")

if __name__ == "__main__":
    main() 