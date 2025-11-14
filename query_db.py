#!/usr/bin/env python3
from database import get_db, Narration
import sys

def show_all():
    narrations = get_db().query(Narration).all()
    if not narrations:
        return print("No narrations found.")
    
    print(f"\n{'ID':<5} {'URL':<50} {'Status':<12} {'Captions':<10} {'Audio':<8}")
    print("-" * 90)
    for n in narrations:
        url = n.url[:47] + "..." if len(n.url) > 50 else n.url
        print(f"{n.id:<5} {url:<50} {n.status:<12} {len(n.image_captions):<10} {len(n.audio_chunks):<8}")
    print()

def show_details(nid):
    n = get_db().query(Narration).filter(Narration.id == nid).first()
    if not n:
        return print(f"Narration #{nid} not found.")
    
    print(f"\nNARRATION #{n.id}\nURL: {n.url}\nStatus: {n.status}\nCreated: {n.created_at}\nText: {len(n.text)} chars")
    print(f"\nImage Captions ({len(n.image_captions)}):")
    for ic in n.image_captions:
        print(f"  - {ic.caption}")
    print(f"\nAudio Chunks ({len(n.audio_chunks)}):")
    for ac in n.audio_chunks:
        print(f"  - Chunk {ac.chunk_number}: {ac.file_path}")
    print()

def delete(nid):
    db = get_db()
    n = db.query(Narration).filter(Narration.id == nid).first()
    if not n:
        return print(f"Narration #{nid} not found.")
    
    if input(f"Delete #{nid}? (yes/no): ").lower() == 'yes':
        db.delete(n)
        db.commit()
        print("Deleted!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_db.py [list|show <id>|delete <id>]")
        sys.exit(1)
    
    cmd, args = sys.argv[1], sys.argv[2:] if len(sys.argv) > 2 else []
    
    if cmd == "list":
        show_all()
    elif cmd == "show" and args:
        show_details(int(args[0]))
    elif cmd == "delete" and args:
        delete(int(args[0]))
    else:
        print("Invalid command")

