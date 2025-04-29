from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_utils import get_db_connection

ingredient_bp = Blueprint('ingredient', __name__)

@api_bp.route('/ingredients', methods=['GET'])
def get_ingredients():
    search = request.args.get('search', '')
    print(f"Searching for ingredients: '{search}'")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT id, name FROM base_ingredients 
            WHERE name ILIKE %s 
            ORDER BY name
        """, (f'%{search}%',))
    else:
        cur.execute("""
            SELECT id, name FROM base_ingredients 
            ORDER BY name LIMIT 50
        """)
    
    ingredients = [{"id": str(row['id']), "name": row['name']} for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    print(f"Found {len(ingredients)} ingredients")
    return jsonify(ingredients)

@api_bp.route('/ingredients', methods=['POST'])
def add_ingredient():
    data = request.json
    print(f"Received add ingredient request with data: {data}")
    
    name = data.get('name')
    
    if not name:
        print("Error: Ingredient name is required")
        return jsonify({"status": "error", "message": "Ingredient name is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Handle user ID for creation
        user_id = None
        if current_user and current_user.is_authenticated:
            user_id = current_user.id
        else:
            # Get a default user ID
            cur.execute("SELECT id FROM users LIMIT 1")
            user_result = cur.fetchone()
            if user_result:
                user_id = user_result['id']
            else:
                print("No users available in the database")
                return jsonify({"status": "error", "message": "No users available"}), 500
        
        # Insert the new base ingredient
        cur.execute("""
            INSERT INTO base_ingredients (name, added_by_user_id, is_verified)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (name, user_id, False))
        
        new_id = cur.fetchone()['id']
        conn.commit()
        
        return jsonify({"status": "success", "message": "Ingredient added", "id": str(new_id)})
    except Exception as e:
        conn.rollback()
        print(f"Error adding ingredient: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Brands API endpoints
@api_bp.route('/brands', methods=['GET'])
def get_brands():
    ingredient_id = request.args.get('ingredient_id')
    search = request.args.get('search', '')
    
    if not ingredient_id:
        return jsonify({"status": "error", "message": "ingredient_id is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if search:
            cur.execute("""
                SELECT b.id, b.name 
                FROM brands b
                JOIN branded_ingredients bi ON b.id = bi.brand_id
                WHERE bi.base_ingredient_id = %s AND b.name ILIKE %s
                ORDER BY b.name
            """, (ingredient_id, f'%{search}%'))
        else:
            cur.execute("""
                SELECT b.id, b.name 
                FROM brands b
                JOIN branded_ingredients bi ON b.id = bi.brand_id
                WHERE bi.base_ingredient_id = %s
                ORDER BY b.name
            """, (ingredient_id,))
            
        brands = [{"id": str(row['id']), "name": row['name']} for row in cur.fetchall()]
        return jsonify(brands)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@api_bp.route('/brands', methods=['POST'])
def add_brand():
    data = request.json
    print(f"Received add brand request with data: {data}")
    
    name = data.get('name')
    ingredient_id = data.get('ingredient_id')
    
    if not name or not ingredient_id:
        print("Error: Name and ingredient_id are required")
        return jsonify({"status": "error", "message": "Name and ingredient_id are required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Handle user ID
        user_id = None
        if current_user and current_user.is_authenticated:
            user_id = current_user.id
        else:
            cur.execute("SELECT id FROM users LIMIT 1")
            user_result = cur.fetchone()
            if user_result:
                user_id = user_result['id']
            else:
                print("No users available in the database")
                return jsonify({"status": "error", "message": "No users available"}), 500
        
        # Create or find the brand
        cur.execute("SELECT id FROM brands WHERE name ILIKE %s", (name,))
        brand = cur.fetchone()
        
        if brand:
            brand_id = brand['id']
            print(f"Found existing brand: {name}, id: {brand_id}")
        else:
            cur.execute("""
                INSERT INTO brands (name, added_by_user_id, is_verified)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (name, user_id, False))
            brand_id = cur.fetchone()['id']
            print(f"Created new brand: {name}, id: {brand_id}")
        
        # Create the branded ingredient
        cur.execute("""
            INSERT INTO branded_ingredients (base_ingredient_id, brand_id, added_by_user_id, is_verified)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (ingredient_id, brand_id, user_id, False))
        
        branded_ingredient_id = cur.fetchone()['id']
        conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Brand and branded ingredient created",
            "brand_id": str(brand_id),
            "branded_ingredient_id": str(branded_ingredient_id)
        })
    except Exception as e:
        conn.rollback()
        print(f"Error adding brand: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Debug endpoint to check table structure
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
