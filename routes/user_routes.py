from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_utils import get_db_connection

user_bp = Blueprint('user', __name__)

@api_bp.route('/user/recipes', methods=['GET'])
@login_required
def get_user_recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT r.id, r.title, r.description, r.servings, r.prep_time_minutes, 
                r.cook_time_minutes, r.is_private, r.created_at, r.updated_at,
                c.name as cuisine_name
            FROM recipes r
            LEFT JOIN cuisines c ON r.cuisine_id = c.id
            WHERE r.created_by_user_id = %s
            ORDER BY r.created_at DESC
        """, (current_user.id,))
        
        recipes = [
            {
                "id": str(row['id']),
                "title": row['title'],
                "description": row['description'],
                "servings": row['servings'],
                "prep_time_minutes": row['prep_time_minutes'],
                "cook_time_minutes": row['cook_time_minutes'],
                "is_private": row['is_private'],
                "cuisine": row['cuisine_name'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
            }
