from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_utils import get_db_connection

upload_bp = Blueprint('upload', __name__)

@api_bp.route('/debug/table-schema', methods=['GET'])
def debug_table_schema():
    table_name = request.args.get('table', 'recipes')
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get table columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cur.fetchall()
        
        result = {
            "table_name": table_name,
            "columns": [{"name": col['column_name'], "type": col['data_type'], "nullable": col['is_nullable']} for col in columns]
        }
