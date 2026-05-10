#!/usr/bin/env python
"""
Vote Management Admin Utility

Equivalent to Django management commands for votes.
Run: python admin_votes.py --action <action> [options]

Actions:
  list        - List all votes with filtering options
  stats       - Show vote statistics
  delete      - Delete a vote by ID
  clear       - Delete all votes (use with caution)
  user-votes  - List votes by a specific user
"""

import sys
import argparse
from datetime import datetime
from database import SessionLocal
from models.vote import Vote
from models.question import Question
from models.answer import Answer
from models.user import User
from sqlalchemy import func


def list_votes(db, limit=100, user_id=None, question_id=None, answer_id=None):
    """List votes with optional filtering"""
    query = db.query(Vote)
    
    if user_id:
        query = query.filter(Vote.user_id == user_id)
    if question_id:
        query = query.filter(Vote.question_id == question_id)
    if answer_id:
        query = query.filter(Vote.answer_id == answer_id)
    
    votes = query.order_by(Vote.created_at.desc()).limit(limit).all()
    
    if not votes:
        print("No votes found.")
        return
    
    print("\n" + "=" * 100)
    print(f"{'ID':<5} {'User':<15} {'Question':<15} {'Answer':<15} {'Created':<20}")
    print("=" * 100)
    
    for vote in votes:
        user = db.query(User).filter(User.id == vote.user_id).first()
        question_id_str = str(vote.question_id) if vote.question_id else "-"
        answer_id_str = str(vote.answer_id) if vote.answer_id else "-"
        created = vote.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{vote.id:<5} {user.username:<15} {question_id_str:<15} {answer_id_str:<15} {created:<20}")
    
    print("=" * 100)
    print(f"Total: {len(votes)} votes\n")


def show_stats(db):
    """Show vote statistics"""
    total_votes = db.query(func.count(Vote.id)).scalar() or 0
    
    question_votes = db.query(func.count(Vote.id)).filter(
        Vote.question_id.isnot(None)
    ).scalar() or 0
    
    answer_votes = db.query(func.count(Vote.id)).filter(
        Vote.answer_id.isnot(None)
    ).scalar() or 0
    
    # Top voted questions
    top_questions = db.query(
        Vote.question_id,
        func.count(Vote.id).label('vote_count')
    ).filter(
        Vote.question_id.isnot(None)
    ).group_by(Vote.question_id).order_by(
        func.count(Vote.id).desc()
    ).limit(5).all()
    
    # Top voted answers
    top_answers = db.query(
        Vote.answer_id,
        func.count(Vote.id).label('vote_count')
    ).filter(
        Vote.answer_id.isnot(None)
    ).group_by(Vote.answer_id).order_by(
        func.count(Vote.id).desc()
    ).limit(5).all()
    
    # Top voters
    top_voters = db.query(
        Vote.user_id,
        func.count(Vote.id).label('vote_count')
    ).group_by(Vote.user_id).order_by(
        func.count(Vote.id).desc()
    ).limit(5).all()
    
    print("\n" + "=" * 80)
    print("VOTE STATISTICS")
    print("=" * 80)
    print(f"Total votes: {total_votes}")
    print(f"  - Question votes: {question_votes}")
    print(f"  - Answer votes: {answer_votes}")
    
    print("\nTop 5 Voted Questions:")
    print("-" * 80)
    for question_id, vote_count in top_questions:
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            title = question.title[:50] + "..." if len(question.title) > 50 else question.title
            print(f"  Q{question_id}: {title} ({vote_count} votes)")
    
    print("\nTop 5 Voted Answers:")
    print("-" * 80)
    for answer_id, vote_count in top_answers:
        answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            body = answer.body[:50] + "..." if len(answer.body) > 50 else answer.body
            print(f"  A{answer_id}: {body} ({vote_count} votes)")
    
    print("\nTop 5 Voters:")
    print("-" * 80)
    for user_id, vote_count in top_voters:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"  {user.username} ({vote_count} votes)")
    
    print("=" * 80 + "\n")


def delete_vote(db, vote_id):
    """Delete a vote by ID"""
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    
    if not vote:
        print(f"✗ Vote with ID {vote_id} not found")
        return False
    
    target = f"Q{vote.question_id}" if vote.question_id else f"A{vote.answer_id}"
    user = db.query(User).filter(User.id == vote.user_id).first()
    
    db.delete(vote)
    db.commit()
    
    print(f"✓ Vote deleted!")
    print(f"  User: {user.username}")
    print(f"  Target: {target}")
    return True


def clear_all_votes(db, confirm=False):
    """Delete all votes (use with caution)"""
    if not confirm:
        print("⚠ WARNING: This will delete ALL votes from the database!")
        response = input("Type 'yes' to confirm: ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return False
    
    count = db.query(func.count(Vote.id)).scalar() or 0
    db.query(Vote).delete()
    db.commit()
    
    print(f"✓ Deleted {count} votes from the database")
    return True


def user_votes(db, user_id):
    """List votes by a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        print(f"✗ User with ID {user_id} not found")
        return
    
    votes = db.query(Vote).filter(Vote.user_id == user_id).all()
    
    print("\n" + "=" * 80)
    print(f"Votes by {user.username} (User ID: {user_id})")
    print("=" * 80)
    
    if not votes:
        print("No votes found.")
        print("=" * 80 + "\n")
        return
    
    question_votes = [v for v in votes if v.question_id]
    answer_votes = [v for v in votes if v.answer_id]
    
    print(f"\nQuestions voted: {len(question_votes)}")
    for vote in question_votes:
        question = db.query(Question).filter(Question.id == vote.question_id).first()
        if question:
            title = question.title[:50] + "..." if len(question.title) > 50 else question.title
            print(f"  Q{vote.question_id}: {title} (voted {vote.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
    
    print(f"\nAnswers voted: {len(answer_votes)}")
    for vote in answer_votes:
        answer = db.query(Answer).filter(Answer.id == vote.answer_id).first()
        if answer:
            body = answer.body[:50] + "..." if len(answer.body) > 50 else answer.body
            print(f"  A{vote.answer_id}: {body} (voted {vote.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
    
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Vote Management Admin Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python admin_votes.py --action list
  python admin_votes.py --action list --limit 50
  python admin_votes.py --action stats
  python admin_votes.py --action user-votes --user-id 1
  python admin_votes.py --action delete --vote-id 5
  python admin_votes.py --action clear
        """
    )
    
    parser.add_argument(
        "--action",
        required=True,
        choices=["list", "stats", "delete", "clear", "user-votes"],
        help="Action to perform"
    )
    
    parser.add_argument("--limit", type=int, default=100, help="Limit results (default: 100)")
    parser.add_argument("--user-id", type=int, help="Filter by user ID")
    parser.add_argument("--question-id", type=int, help="Filter by question ID")
    parser.add_argument("--answer-id", type=int, help="Filter by answer ID")
    parser.add_argument("--vote-id", type=int, help="Vote ID to delete")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        if args.action == "list":
            list_votes(
                db,
                limit=args.limit,
                user_id=args.user_id,
                question_id=args.question_id,
                answer_id=args.answer_id
            )
        
        elif args.action == "stats":
            show_stats(db)
        
        elif args.action == "delete":
            if not args.vote_id:
                print("Error: --vote-id is required for delete action")
                sys.exit(1)
            delete_vote(db, args.vote_id)
        
        elif args.action == "clear":
            clear_all_votes(db, args.confirm)
        
        elif args.action == "user-votes":
            if not args.user_id:
                print("Error: --user-id is required for user-votes action")
                sys.exit(1)
            user_votes(db, args.user_id)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
