import json

def convert_author_abstracts():
    """Convert author_abstracts.json to a new format with id, name, 3 research papers, and connections"""
    
    # Load the original data
    with open("nicolasdata/author_abstracts_4.json", "r") as f:
        data = json.load(f)
    
    # Extract the components
    all_authors = data.get("all_authors", [])
    author_names = data.get("author_names", {})
    co_authors = data.get("co_authors", {})
    author_abstracts = data.get("author_abstracts", {})
    
    # Convert to new format
    converted_data = []
    
    for author_id in all_authors:
        author_name = author_names.get(author_id, "Unknown")
        
        # Get research papers from author_abstracts
        papers = author_abstracts.get(author_id, [])
        # Sort by year (most recent first), then take top 3
        sorted_papers = sorted(papers, key=lambda x: x.get("year", 0), reverse=True)[:3]
        
        # Format papers
        formatted_papers = []
        for paper in sorted_papers:
            formatted_papers.append({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "year": paper.get("year", 0),
                "authors": paper.get("authors", "")
            })
        
        # Get connections (co-authors)
        connections = co_authors.get(author_id, [])
        
        # Create the new entry
        entry = {
            "id": author_id,
            "name": author_name,
            "research_papers": formatted_papers,
            "connections": connections
        }
        
        converted_data.append(entry)
    
    # Save the converted data
    output_file = "fornicolas.json"
    with open(output_file, "w") as f:
        json.dump(converted_data, f, indent=2)
    
    print(f"✅ Converted {len(converted_data)} authors")
    print(f"📊 Output saved to: {output_file}")
    
    # Show a sample entry
    if converted_data:
        print("\n📋 Sample entry:")
        sample = converted_data[0]
        print(f"ID: {sample['id']}")
        print(f"Name: {sample['name']}")
        print(f"Papers: {len(sample['research_papers'])}")
        print(f"Connections: {len(sample['connections'])}")
        
        if sample['research_papers']:
            print(f"First paper: {sample['research_papers'][0]['title'][:50]}...")

if __name__ == "__main__":
    convert_author_abstracts() 