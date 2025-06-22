import json
import glob
import os

def merge_author_abstracts():
    """Merge multiple author_abstracts*.json files and convert to force graph format"""
    
    # Find all author abstracts files
    abstract_files = glob.glob("author_abstracts*.json")
    print(f"📁 Found {len(abstract_files)} author abstracts files: {abstract_files}")
    
    if not abstract_files:
        print("❌ No author_abstracts*.json files found!")
        return
    
    # Initialize merged data structure
    merged_data = {
        "input_authors": [],
        "all_authors": [],
        "author_names": {},
        "co_authors": {},
        "author_abstracts": {}
    }
    
    # Process each file
    for file_path in abstract_files:
        print(f"\n📖 Processing {file_path}...")
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Merge input_authors (unique)
        input_authors = data.get("input_authors", [])
        for author_id in input_authors:
            if author_id not in merged_data["input_authors"]:
                merged_data["input_authors"].append(author_id)
        
        # Merge all_authors (unique)
        all_authors = data.get("all_authors", [])
        for author_id in all_authors:
            if author_id not in merged_data["all_authors"]:
                merged_data["all_authors"].append(author_id)
        
        # Merge author_names (later files override earlier ones)
        author_names = data.get("author_names", {})
        merged_data["author_names"].update(author_names)
        
        # Merge co_authors (combine lists, remove duplicates)
        co_authors = data.get("co_authors", {})
        for author_id, connections in co_authors.items():
            if author_id not in merged_data["co_authors"]:
                merged_data["co_authors"][author_id] = []
            # Add new connections
            for conn in connections:
                if conn not in merged_data["co_authors"][author_id]:
                    merged_data["co_authors"][author_id].append(conn)
        
        # Merge author_abstracts (later files override earlier ones)
        author_abstracts = data.get("author_abstracts", {})
        for author_id, papers in author_abstracts.items():
            if author_id not in merged_data["author_abstracts"]:
                merged_data["author_abstracts"][author_id] = []
            # Add new papers (avoid duplicates by title)
            existing_titles = {paper.get("title", "") for paper in merged_data["author_abstracts"][author_id]}
            for paper in papers:
                if paper.get("title", "") not in existing_titles:
                    merged_data["author_abstracts"][author_id].append(paper)
    
    print(f"\n📊 Merged data summary:")
    print(f"  - Input authors: {len(merged_data['input_authors'])}")
    print(f"  - All authors: {len(merged_data['all_authors'])}")
    print(f"  - Author names: {len(merged_data['author_names'])}")
    print(f"  - Co-authors: {len(merged_data['co_authors'])}")
    print(f"  - Author abstracts: {len(merged_data['author_abstracts'])}")
    
    # Save merged data
    merged_file = "merged_author_abstracts.json"
    with open(merged_file, "w") as f:
        json.dump(merged_data, f, indent=2)
    print(f"\n💾 Saved merged data to: {merged_file}")
    
    return merged_data

def convert_merged_to_author_data(merged_data):
    """Convert merged data to the author data format"""
    
    print("\n🔄 Converting to author data format...")
    
    # Convert to new format
    converted_data = []
    
    for author_id in merged_data["all_authors"]:
        author_name = merged_data["author_names"].get(author_id, "Unknown")
        
        # Get research papers from author_abstracts
        papers = merged_data["author_abstracts"].get(author_id, [])
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
        connections = merged_data["co_authors"].get(author_id, [])
        
        # Create the new entry
        entry = {
            "id": author_id,
            "name": author_name,
            "research_papers": formatted_papers,
            "connections": connections
        }
        
        converted_data.append(entry)
    
    # Save the converted data
    output_file = "converted_author_data.json"
    with open(output_file, "w") as f:
        json.dump(converted_data, f, indent=2)
    
    print(f"✅ Converted {len(converted_data)} authors")
    print(f"📊 Output saved to: {output_file}")
    
    return converted_data

def convert_to_forcegraph():
    """Convert author data to force graph format"""
    
    print("\n🌐 Converting to force graph format...")
    
    # Load the converted author data
    with open("converted_author_data.json", "r") as f:
        authors = json.load(f)

    # Build nodes
    nodes = []
    id_to_node = {}
    for author in authors:
        node = {
            "id": author["id"],
            "name": author["name"],
        }
        nodes.append(node)
        id_to_node[author["id"]] = node

    # Build links (deduplicate, undirected)
    links_set = set()
    links = []
    for author in authors:
        source_id = author["id"]
        for target_id in author.get("connections", []):
            # Only add link if both nodes exist
            if target_id in id_to_node:
                # Use tuple with sorted ids to deduplicate undirected links
                link_tuple = tuple(sorted([source_id, target_id]))
                if link_tuple not in links_set:
                    links_set.add(link_tuple)
                    links.append({"source": link_tuple[0], "target": link_tuple[1]})

    # Output
    out = {"nodes": nodes, "links": links}
    with open("forcegraph_data.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"✅ Wrote {len(nodes)} nodes and {len(links)} links to forcegraph_data.json")

def main():
    """Main function to run the complete pipeline"""
    print("🚀 Starting merge and update pipeline...")
    
    # Step 1: Merge all author abstracts files
    merged_data = merge_author_abstracts()
    
    # Step 2: Convert to author data format
    convert_merged_to_author_data(merged_data)
    
    # Step 3: Convert to force graph format
    convert_to_forcegraph()
    
    print("\n🎉 Pipeline complete! Your force graph is ready to view.")
    print("💡 Run 'python -m http.server 8000' and visit http://localhost:8000/force_graph.html")

if __name__ == "__main__":
    main() 