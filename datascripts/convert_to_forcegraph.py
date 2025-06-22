import json

def convert_to_forcegraph():
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
            # Optionally add more fields here (e.g., research_papers)
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

if __name__ == "__main__":
    convert_to_forcegraph() 