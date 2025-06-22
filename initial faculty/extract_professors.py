from bs4 import BeautifulSoup
import json
import re

def extract_professors_from_html(html_file):
    """
    Extract professor names and interests from the HTML file.
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

def save_professors_to_file(professors, output_file):
    """
    Save professors data to a file in JSON format.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(professors)} professors to {output_file}")

def save_professors_to_python_array(professors, output_file):
    """
    Save professors data to a Python file as an array.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Professors data extracted from batch1.html\n")
        f.write("professors = [\n")
        
        for i, professor in enumerate(professors):
            f.write("    {\n")
            f.write(f'        "name": "{professor["name"]}",\n')
            f.write('        "interests": [\n')
            
            for j, interest in enumerate(professor["interests"]):
                if j == len(professor["interests"]) - 1:
                    f.write(f'            "{interest}"\n')
                else:
                    f.write(f'            "{interest}",\n')
            
            if i == len(professors) - 1:
                f.write("        ]\n")
                f.write("    }\n")
            else:
                f.write("        ]\n")
                f.write("    },\n")
        
        f.write("]\n")
        f.write(f"\n# Total professors: {len(professors)}\n")
    
    print(f"Saved {len(professors)} professors to {output_file}")

def print_summary(professors):
    """
    Print a summary of the extracted data.
    """
    print(f"\n=== SUMMARY ===")
    print(f"Total professors found: {len(professors)}")
    
    # Count total interests
    total_interests = sum(len(prof['interests']) for prof in professors)
    print(f"Total interests found: {total_interests}")
    
    # Show first few professors as example
    print(f"\n=== FIRST 3 PROFESSORS ===")
    for i, professor in enumerate(professors[:3]):
        print(f"{i+1}. {professor['name']}")
        print(f"   Interests: {', '.join(professor['interests'])}")
        print()

def main():
    # Extract professors from batch1.html
    print("Extracting professors from batch1.html...")
    professors = extract_professors_from_html('batch1.html')
    
    if not professors:
        print("No professors found in the HTML file!")
        return
    
    # Print summary
    print_summary(professors)
    
    # Save to JSON file
    save_professors_to_file(professors, 'professors_data.json')
    
    # Save to Python array file
    save_professors_to_python_array(professors, 'professors_array.py')
    
    print("\n=== EXTRACTION COMPLETE ===")
    print("Files created:")
    print("- professors_data.json (JSON format)")
    print("- professors_array.py (Python array format)")

if __name__ == "__main__":
    main() 