"""
Admin Management Script for Tags

This script provides utilities for managing tags in the IUBAT QA Platform.
Unlike Django's admin.py, FastAPI uses Python scripts for administrative tasks.

Usage:
    python admin_tags.py --action list
    python admin_tags.py --action create --name "Django" --slug "django"
    python admin_tags.py --action delete --id 1
"""

import sys
import argparse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.tag import Tag


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def list_tags(db: Session):
    """List all tags"""
    tags = db.query(Tag).all()
    
    if not tags:
        print("No tags found")
        return
    
    print("\n" + "="*60)
    print(f"{'ID':<5} {'Name':<20} {'Slug':<20}")
    print("="*60)
    
    for tag in tags:
        print(f"{tag.id:<5} {tag.name:<20} {tag.slug:<20}")
    
    print("="*60)
    print(f"Total: {len(tags)} tags\n")


def create_tag(db: Session, name: str, slug: str):
    """Create a new tag"""
    # Check if tag already exists
    existing = db.query(Tag).filter(
        (Tag.name == name) | (Tag.slug == slug)
    ).first()
    
    if existing:
        print(f"✗ Error: Tag with name '{name}' or slug '{slug}' already exists")
        return
    
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    print(f"✓ Tag created successfully!")
    print(f"  ID: {tag.id}")
    print(f"  Name: {tag.name}")
    print(f"  Slug: {tag.slug}")


def update_tag(db: Session, tag_id: int, name: str = None, slug: str = None):
    """Update an existing tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        print(f"✗ Error: Tag with ID {tag_id} not found")
        return
    
    if name:
        # Check if name already exists
        existing = db.query(Tag).filter(
            Tag.name == name,
            Tag.id != tag_id
        ).first()
        if existing:
            print(f"✗ Error: Tag with name '{name}' already exists")
            return
        tag.name = name
    
    if slug:
        # Check if slug already exists
        existing = db.query(Tag).filter(
            Tag.slug == slug,
            Tag.id != tag_id
        ).first()
        if existing:
            print(f"✗ Error: Tag with slug '{slug}' already exists")
            return
        tag.slug = slug
    
    db.commit()
    db.refresh(tag)
    
    print(f"✓ Tag updated successfully!")
    print(f"  ID: {tag.id}")
    print(f"  Name: {tag.name}")
    print(f"  Slug: {tag.slug}")


def delete_tag(db: Session, tag_id: int):
    """Delete a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        print(f"✗ Error: Tag with ID {tag_id} not found")
        return
    
    tag_name = tag.name
    db.delete(tag)
    db.commit()
    
    print(f"✓ Tag '{tag_name}' deleted successfully!")


def get_tag_stats(db: Session):
    """Get statistics about tags"""
    from models.question import Question
    
    tags = db.query(Tag).all()
    
    print("\n" + "="*70)
    print(f"{'ID':<5} {'Name':<20} {'Slug':<20} {'Questions':<15}")
    print("="*70)
    
    for tag in tags:
        questions_count = db.query(Question.id).join(
            Question.tags
        ).filter(Tag.id == tag.id).count()
        
        print(f"{tag.id:<5} {tag.name:<20} {tag.slug:<20} {questions_count:<15}")
    
    print("="*70)
    print(f"Total tags: {len(tags)}\n")


def bulk_create_tags(db: Session, tags_list: list):
    """Create multiple tags at once
    
    tags_list: List of dicts with 'name' and 'slug' keys
    Example: [
        {"name": "Django", "slug": "django"},
        {"name": "FastAPI", "slug": "fastapi"},
    ]
    """
    created_count = 0
    
    for tag_data in tags_list:
        name = tag_data.get('name')
        slug = tag_data.get('slug')
        
        if not name or not slug:
            print(f"✗ Skipping invalid tag data: {tag_data}")
            continue
        
        # Check if tag already exists
        existing = db.query(Tag).filter(
            (Tag.name == name) | (Tag.slug == slug)
        ).first()
        
        if existing:
            print(f"⊘ Tag '{name}' already exists, skipping")
            continue
        
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        created_count += 1
    
    if created_count > 0:
        db.commit()
        print(f"✓ Successfully created {created_count} tags!")
    else:
        print("No new tags created")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="IUBAT QA Platform - Tag Management"
    )
    parser.add_argument(
        "--action",
        choices=["list", "create", "update", "delete", "stats", "init"],
        required=True,
        help="Action to perform"
    )
    parser.add_argument("--id", type=int, help="Tag ID")
    parser.add_argument("--name", help="Tag name")
    parser.add_argument("--slug", help="Tag slug")
    
    args = parser.parse_args()
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        if args.action == "init":
            create_tables()
        
        elif args.action == "list":
            list_tags(db)
        
        elif args.action == "create":
            if not args.name or not args.slug:
                print("✗ Error: --name and --slug are required for create action")
                sys.exit(1)
            create_tag(db, args.name, args.slug)
        
        elif args.action == "update":
            if not args.id:
                print("✗ Error: --id is required for update action")
                sys.exit(1)
            if not args.name and not args.slug:
                print("✗ Error: At least --name or --slug required for update action")
                sys.exit(1)
            update_tag(db, args.id, args.name, args.slug)
        
        elif args.action == "delete":
            if not args.id:
                print("✗ Error: --id is required for delete action")
                sys.exit(1)
            delete_tag(db, args.id)
        
        elif args.action == "stats":
            get_tag_stats(db)
    
    finally:
        db.close()


# Default tags for initialization
DEFAULT_TAGS = [
    {"name": "Python", "slug": "python"},
    {"name": "Django", "slug": "django"},
    {"name": "FastAPI", "slug": "fastapi"},
    {"name": "REST API", "slug": "rest-api"},
    {"name": "Database", "slug": "database"},
    {"name": "SQL", "slug": "sql"},
    {"name": "Authentication", "slug": "authentication"},
    {"name": "Testing", "slug": "testing"},
    {"name": "Deployment", "slug": "deployment"},
    {"name": "Performance", "slug": "performance"},
    {"name": "Security", "slug": "security"},
    {"name": "Docker", "slug": "docker"},
    {"name": "WebSockets", "slug": "websockets"},
    {"name": "Caching", "slug": "caching"},
    {"name": "Debugging", "slug": "debugging"},
]


if __name__ == "__main__":
    main()
