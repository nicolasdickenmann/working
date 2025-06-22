#!/usr/bin/env python3
"""
Convert author_abstracts_4.json to force graph format
Creates nodes and links for 3D force-directed graph visualization
"""

import json
import os

def convert_author_abstracts_4_to_graph(input_file, output_file):
    """
    Convert author_abstracts_4.json to force graph format
    
    Args:
        input_file (str): Path to author_abstracts_4.json
        output_file (str): Path to output force graph JSON
    """
    
    print(f"📖 Loading data from {input_file}...")
    
    # Load the author abstracts data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract components
    author_names = data.get('author_names', {})
    co_authors = data.get('co_authors', {})
    author_abstracts = data.get('author_abstracts', {})
    author_levels = data.get('author_levels', {})
    summary = data.get('summary', {})
    
    print(f"📊 Data summary:")
    print(f"  - Total authors: {summary.get('total_authors', 0)}")
    print(f"  - Input authors: {summary.get('input_authors_count', 0)}")
    print(f"  - Direct co-authors: {summary.get('direct_co_authors_count', 0)}")
    print(f"  - Second level co-authors: {summary.get('second_level_co_authors_count', 0)}")
    print(f"  - Authors with abstracts: {summary.get('authors_with_abstracts', 0)}")
    print(f"  - Total abstracts: {summary.get('total_abstracts', 0)}")
    
    # Build nodes
    print("\n🔨 Building nodes...")
    nodes = []
    id_to_node = {}
    
    for author_id, author_name in author_names.items():
        # Get research papers for this author
        papers = author_abstracts.get(author_id, [])
        
        # Get top 3 most recent papers
        sorted_papers = sorted(papers, key=lambda x: x.get('year', 0), reverse=True)[:3]
        
        # Format papers for display
        formatted_papers = []
        for paper in sorted_papers:
            formatted_papers.append({
                "title": paper.get('title', ''),
                "abstract": paper.get('abstract', ''),
                "year": paper.get('year', 0),
                "authors": paper.get('authors', '')
            })
        
        # Determine author level for styling
        author_level = "unknown"
        if author_id in author_levels.get('input_authors', []):
            author_level = "input"
        elif author_id in author_levels.get('direct_co_authors', []):
            author_level = "direct"
        elif author_id in author_levels.get('second_level_co_authors', []):
            author_level = "second"
        
        # Create node
        node = {
            "id": author_id,
            "name": author_name,
            "level": author_level,
            "papers": formatted_papers,
            "paper_count": len(papers)
        }
        
        nodes.append(node)
        id_to_node[author_id] = node
    
    print(f"✅ Created {len(nodes)} nodes")
    
    # Build links (co-authorship connections)
    print("\n🔗 Building links...")
    links_set = set()  # To avoid duplicate links
    links = []
    
    for author_id, connections in co_authors.items():
        # Only process if this author exists in our nodes
        if author_id not in id_to_node:
            continue
            
        for target_id in connections:
            # Only add link if both nodes exist
            if target_id in id_to_node:
                # Use tuple with sorted ids to deduplicate undirected links
                link_tuple = tuple(sorted([author_id, target_id]))
                if link_tuple not in links_set:
                    links_set.add(link_tuple)
                    links.append({
                        "source": link_tuple[0],
                        "target": link_tuple[1]
                    })
    
    print(f"✅ Created {len(links)} links")
    
    # Create the force graph data structure
    force_graph_data = {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "source_file": input_file,
            "total_authors": len(nodes),
            "total_connections": len(links),
            "summary": summary
        }
    }
    
    # Save to output file
    print(f"\n💾 Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(force_graph_data, f, indent=2)
    
    print(f"✅ Successfully converted to force graph format!")
    print(f"📁 Output saved to: {output_file}")
    
    # Print some statistics
    print(f"\n📊 Final graph statistics:")
    print(f"  - Nodes: {len(nodes)}")
    print(f"  - Links: {len(links)}")
    print(f"  - Input authors: {len([n for n in nodes if n['level'] == 'input'])}")
    print(f"  - Direct co-authors: {len([n for n in nodes if n['level'] == 'direct'])}")
    print(f"  - Second level co-authors: {len([n for n in nodes if n['level'] == 'second'])}")
    
    return force_graph_data

def main():
    """Main function"""
    print("🚀 Converting author_abstracts_5.json to force graph format")
    print("=" * 60)
    
    # File paths
    input_file = "nicolasdata/author_abstracts_5.json"
    output_file = "static/forcegraph_data_3.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Convert the data
    try:
        force_graph_data = convert_author_abstracts_4_to_graph(input_file, output_file)
        print(f"\n🎉 Conversion complete!")
        print(f"💡 You can now use {output_file} with your 3D force graph visualization")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return

if __name__ == "__main__":
    main() 