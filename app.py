from flask import Flask, redirect, url_for, render_template, Blueprint, request, jsonify
from flask_login import LoginManager, current_user, login_required
import os
import uuid
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from flask_cors import CORS


# Import the database connection from db_utils
from db_utils import get_db_connection

# Load environment variables
load_dotenv()

# Create Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"], allow_headers=["Content-Type", "Authorization"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import modules - these imports now come after the db_utils import
from auth import User, auth_bp
from admin import admin_bp

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/recipes', methods=['POST'])
@login_required  # Make sure this decorator is present
def create_recipe():
    data = request.json
    print(f"Received recipe data: {data}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Begin transaction
        print("Starting transaction...")
        cur.execute("BEGIN")
        
        # Get authenticated user ID - with better error handling
        if not current_user or not current_user.is_authenticated:
            print("WARNING: No authenticated user found, using fallback")
            # Optional fallback for debugging only - remove in production
            cur.execute("SELECT id FROM users WHERE role = 'user' LIMIT 1")
            user_result = cur.fetchone()
            if not user_result:
                raise Exception("No authenticated user and no fallback user available")
            user_id = user_result['id']
        else:
            user_id = current_user.id
            
        print(f"Creating recipe for user ID: {user_id}")
        
        # Insert recipe with proper user ID, including main image
        print("Inserting recipe...")
        cur.execute("""
            INSERT INTO recipes (title, description, servings, created_by_user_id, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('name'),
            data.get('story', ''), 
            data.get('servings', 2),
            user_id,
            data.get('image')  # Include main recipe image
        ))
        
        recipe_id = cur.fetchone()['id']
        print(f"Recipe created with ID: {recipe_id}")
        
        # Insert ingredients
        for idx, ingredient in enumerate(data.get('ingredients', [])):
            # Get base ingredient ID by name
            cur.execute("SELECT id FROM base_ingredients WHERE name ILIKE %s", (ingredient.get('name'),))
            base_ingredient = cur.fetchone()
            
            if not base_ingredient:
                # If ingredient doesn't exist, create it
                cur.execute("""
                    INSERT INTO base_ingredients (name, is_verified, added_by_user_id)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (
                    ingredient.get('name'),
                    False,
                    user_id
                ))
                base_ingredient_id = cur.fetchone()['id']
            else:
                base_ingredient_id = base_ingredient['id']
            
            # Handle brand if provided
            brand_id = None
            if ingredient.get('brand'):
                # Try to find the brand
                cur.execute("SELECT id FROM brands WHERE name ILIKE %s", (ingredient.get('brand'),))
                brand = cur.fetchone()
                
                if not brand:
                    # Create the brand if it doesn't exist
                    cur.execute("""
                        INSERT INTO brands (name, is_verified, added_by_user_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        ingredient.get('brand'),
                        False,
                        user_id
                    ))
                    brand_id = cur.fetchone()['id']
                else:
                    brand_id = brand['id']
            else:
                # Create or get a default "Generic" brand
                cur.execute("SELECT id FROM brands WHERE name = 'Generic'")
                generic_brand = cur.fetchone()
                
                if not generic_brand:
                    # Create generic brand if it doesn't exist
                    cur.execute("""
                        INSERT INTO brands (name, is_verified, added_by_user_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        'Generic',
                        True,
                        user_id
                    ))
                    brand_id = cur.fetchone()['id']
                else:
                    brand_id = generic_brand['id']
            
            # Get or create branded_ingredient entry
            cur.execute("""
                SELECT id FROM branded_ingredients 
                WHERE base_ingredient_id = %s AND brand_id = %s
            """, (base_ingredient_id, brand_id))
            branded_ingredient = cur.fetchone()
            
            if not branded_ingredient:
                # Create the branded ingredient if it doesn't exist
                cur.execute("""
                    INSERT INTO branded_ingredients (base_ingredient_id, brand_id, is_verified, added_by_user_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    base_ingredient_id,
                    brand_id,
                    False,
                    user_id
                ))
                branded_ingredient_id = cur.fetchone()['id']
            else:
                branded_ingredient_id = branded_ingredient['id']
            
            # Insert the recipe ingredient with the correct branded_ingredient_id
            cur.execute("""
                INSERT INTO recipe_ingredients (recipe_id, branded_ingredient_id, quantity, display_order)
                VALUES (%s, %s, %s, %s)
            """, (
                recipe_id,
                branded_ingredient_id,
                ingredient.get('quantity', ''),
                idx  # Use idx as display_order
            ))
        
        # Insert steps with updated image handling
        for idx, step in enumerate(data.get('steps', [])):
            # Use stepImage directly from the step object
            step_image = step.get('stepImage')
            media_type = 'image' if step_image else None
            
            cur.execute("""
                INSERT INTO recipe_steps (recipe_id, step_number, description, media_url, media_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                recipe_id,
                idx + 1,
                step.get('instruction', ''),
                step_image,  # Use the image path directly
                media_type
            ))
        
        # Commit transaction
        cur.execute("COMMIT")
        print("Recipe transaction committed successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Recipe created successfully", 
            "id": str(recipe_id)
        })
        
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"Error saving recipe: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(traceback.format_exc())  # This will print the full traceback
        return jsonify({"status": "error", "message": f"Failed to save recipe: {str(e)}"}), 500
    
    finally:
        cur.close()
        conn.close()


# Modified to use string parameter instead of UUID type converter
@api_bp.route('/recipes/<recipe_id>', methods=['PUT'])
@login_required
def update_recipe(recipe_id):
    data = request.json
    print(f"Received recipe update data: {data}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Begin transaction
        print("Starting transaction...")
        cur.execute("BEGIN")
        
        # Convert string to UUID for validation, then back to string for query
        try:
            uuid_obj = uuid.UUID(recipe_id)
            recipe_id_str = str(uuid_obj)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid recipe ID format"}), 400
        
        # Use string representation in queries
        cur.execute("""
            SELECT created_by_user_id FROM recipes
            WHERE id = %s
        """, (recipe_id_str,))
        
        recipe = cur.fetchone()
        if not recipe:
            return jsonify({"status": "error", "message": "Recipe not found"}), 404
            
        if str(recipe['created_by_user_id']) != str(current_user.id):
            return jsonify({"status": "error", "message": "You don't have permission to edit this recipe"}), 403
        
        # Update basic recipe information
        cur.execute("""
            UPDATE recipes
            SET title = %s, description = %s, servings = %s, image_url = %s, updated_at = NOW()
            WHERE id = %s
        """, (
            data.get('name'),
            data.get('story', ''),
            data.get('servings', 2),
            data.get('image'),
            recipe_id_str
        ))
        
        # Delete existing ingredients and steps to replace them
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id_str,))
        cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (recipe_id_str,))
        
        # Re-insert ingredients
        for idx, ingredient in enumerate(data.get('ingredients', [])):
            # Get base ingredient ID by name
            cur.execute("SELECT id FROM base_ingredients WHERE name ILIKE %s", (ingredient.get('name'),))
            base_ingredient = cur.fetchone()
            
            if not base_ingredient:
                # If ingredient doesn't exist, create it
                cur.execute("""
                    INSERT INTO base_ingredients (name, is_verified, added_by_user_id)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (
                    ingredient.get('name'),
                    False,
                    current_user.id
                ))
                base_ingredient_id = cur.fetchone()['id']
            else:
                base_ingredient_id = base_ingredient['id']
            
            # Handle brand if provided
            brand_id = None
            if ingredient.get('brand'):
                # Try to find the brand
                cur.execute("SELECT id FROM brands WHERE name ILIKE %s", (ingredient.get('brand'),))
                brand = cur.fetchone()
                
                if not brand:
                    # Create the brand if it doesn't exist
                    cur.execute("""
                        INSERT INTO brands (name, is_verified, added_by_user_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        ingredient.get('brand'),
                        False,
                        current_user.id
                    ))
                    brand_id = cur.fetchone()['id']
                else:
                    brand_id = brand['id']
            else:
                # Create or get a default "Generic" brand
                cur.execute("SELECT id FROM brands WHERE name = 'Generic'")
                generic_brand = cur.fetchone()
                
                if not generic_brand:
                    # Create generic brand if it doesn't exist
                    cur.execute("""
                        INSERT INTO brands (name, is_verified, added_by_user_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        'Generic',
                        True,
                        current_user.id
                    ))
                    brand_id = cur.fetchone()['id']
                else:
                    brand_id = generic_brand['id']
            
            # Get or create branded_ingredient entry
            cur.execute("""
                SELECT id FROM branded_ingredients 
                WHERE base_ingredient_id = %s AND brand_id = %s
            """, (base_ingredient_id, brand_id))
            branded_ingredient = cur.fetchone()
            
            if not branded_ingredient:
                # Create the branded ingredient if it doesn't exist
                cur.execute("""
                    INSERT INTO branded_ingredients (base_ingredient_id, brand_id, is_verified, added_by_user_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    base_ingredient_id,
                    brand_id,
                    False,
                    current_user.id
                ))
                branded_ingredient_id = cur.fetchone()['id']
            else:
                branded_ingredient_id = branded_ingredient['id']
            
            # Insert the recipe ingredient with the correct branded_ingredient_id
            cur.execute("""
                INSERT INTO recipe_ingredients (recipe_id, branded_ingredient_id, quantity, display_order)
                VALUES (%s, %s, %s, %s)
            """, (
                recipe_id_str,  # Use string representation
                branded_ingredient_id,
                ingredient.get('quantity', ''),
                idx  # Use idx as display_order
            ))
        
        # Insert steps
        for idx, step in enumerate(data.get('steps', [])):
            step_image = step.get('stepImage')
            media_type = 'image' if step_image else None
            
            cur.execute("""
                INSERT INTO recipe_steps (recipe_id, step_number, description, media_url, media_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                recipe_id_str,  # Use string representation
                idx + 1,
                step.get('instruction', ''),
                step_image,
                media_type
            ))
        
        # Commit transaction
        cur.execute("COMMIT")
        print("Recipe update transaction committed successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Recipe updated successfully", 
            "id": recipe_id_str  # Return string representation
        })
        
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"Error updating recipe: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": f"Failed to update recipe: {str(e)}"}), 500
    
    finally:
        cur.close()
        conn.close()

		
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
            for row in cur.fetchall()
        ]
        
        return jsonify(recipes)
    except Exception as e:
        print(f"Error fetching user recipes: {str(e)}")
        return jsonify([]), 500
    finally:
        cur.close()
        conn.close()

# Ingredients endpoints
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
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cur.close()
        conn.close()

# Function to create admin user if it doesn't exist
def create_admin_user():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if admin user exists
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    result = cur.fetchone()
    count = result['count'] if result else 0  # Access by column name, not index
    
    if count == 0:
        # Create a fresh password hash for 'admin123'
        password_hash = generate_password_hash('admin123')
        print(f"Generated new password hash: {password_hash}")
        
        try:
            cur.execute(
                '''
                INSERT INTO users (email, phone, password_hash, first_name, last_name, role, preferred_language)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                ''',
                ('admin@recipekeeper.com', '+910000000000', password_hash, 'Admin', 'User', 'admin', 'en')
            )
            conn.commit()
            print("Admin user created successfully with email: admin@recipekeeper.com and password: admin123")
        except Exception as e:
            conn.rollback()
            print(f"Error creating admin user: {str(e)}")
    
    cur.close()
    conn.close()


# Family API endpoints
@api_bp.route('/families', methods=['GET'])
@login_required
def get_families():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all families where the current user is a member
    cur.execute("""
        SELECT f.id, f.name, f.created_at, fm.role as user_role
        FROM families f
        JOIN family_members fm ON f.id = fm.family_id
        WHERE fm.user_id = %s AND fm.is_active = true
        ORDER BY f.created_at DESC
    """, (current_user.id,))
    
    families = [
        {
            "id": str(row['id']),
            "name": row['name'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "user_role": row['user_role']
        }
        for row in cur.fetchall()
    ]
    
    cur.close()
    conn.close()
    
    return jsonify(families)
	
	
@api_bp.route('/families/<family_id>/members', methods=['POST'])
@login_required
def add_family_member(family_id):
    data = request.json
    email = data.get('email')
    name = data.get('name')
    phone = data.get('phone')
    relation = data.get('relation')
    
    if not email or not name:
        return jsonify({"status": "error", "message": "Email and name are required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Convert family_id to UUID
        try:
            family_uuid = uuid.UUID(family_id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid family ID format"}), 400
            
        # Verify current user is an admin of this family
        cur.execute("""
            SELECT role FROM family_members
            WHERE family_id = %s AND user_id = %s AND is_active = true
        """, (family_uuid, current_user.id))
        
        user_role = cur.fetchone()
        if not user_role or user_role['role'] != 'admin':
            return jsonify({"status": "error", "message": "Only family admins can add members"}), 403
        
        # Check if we've reached the maximum number of members (4)
        cur.execute("""
            SELECT COUNT(*) as count FROM family_members
            WHERE family_id = %s AND is_active = true
        """, (family_uuid,))
        
        member_count = cur.fetchone()['count']
        if member_count >= 4:
            return jsonify({
                "status": "error", 
                "message": "Maximum of 4 family members reached"
            }), 400
        
        # Check if the user exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cur.fetchone()
        
        # Generate invitation token
        invitation_token = str(uuid.uuid4())
        
        if not user_result:
            # Create a pending member entry
            # Parse the name into first and last names
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            cur.execute("""
                INSERT INTO family_members 
                (family_id, user_id, role, relationship, invitation_status, invitation_token, first_name, last_name, email, phone)
                VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, joined_at
            """, (
                family_uuid, 
                'member',
                relation,
                'pending',
                invitation_token,
                first_name,
                last_name,
                email,
                phone
            ))
            
            result = cur.fetchone()
            
            # TODO: Send invitation email with the token
            # For now, we'll just return success
            
            conn.commit()
            
            return jsonify({
                "status": "success", 
                "message": "Invitation sent to user",
                "pending": True
            })
        
        # If user exists
        user_id = user_result['id']
        
        # Check if user is already a member
        cur.execute("""
            SELECT id FROM family_members
            WHERE family_id = %s AND user_id = %s
        """, (family_uuid, user_id))
        
        if cur.fetchone():
            return jsonify({"status": "error", "message": "User is already a member of this family"}), 400
        
        # Add the member
        cur.execute("""
            INSERT INTO family_members 
            (family_id, user_id, role, relationship, invitation_status, invitation_token)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, joined_at
        """, (
            family_uuid, 
            user_id, 
            'member',
            relation,
            'pending',
            invitation_token
        ))
        
        result = cur.fetchone()
        member_id = result['id']
        joined_at = result['joined_at']
        
        # Get user details
        cur.execute("SELECT email, first_name, last_name FROM users WHERE id = %s", (user_id,))
        user_details = cur.fetchone()
        
        # TODO: Send invitation email with the token
        
        conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Invitation sent successfully",
            "member": {
                "id": str(member_id),
                "user_id": str(user_id),
                "role": "member",
                "relationship": relation,
                "invitation_status": "pending",
                "joined_at": joined_at.isoformat() if joined_at else None,
                "email": user_details['email'],
                "first_name": user_details['first_name'],
                "last_name": user_details['last_name']
            }
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@api_bp.route('/families', methods=['POST'])
@login_required
def create_family():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"status": "error", "message": "Family name is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create new family
        cur.execute("""
            INSERT INTO families (name, created_by_user_id)
            VALUES (%s, %s)
            RETURNING id, created_at
        """, (name, current_user.id))
        
        result = cur.fetchone()
        family_id = result['id']
        created_at = result['created_at']
        
        # Add current user as family admin
        cur.execute("""
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (%s, %s, %s)
        """, (family_id, current_user.id, 'admin'))
        
        conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Family created successfully",
            "family": {
                "id": str(family_id),
                "name": name,
                "created_at": created_at.isoformat() if created_at else None,
                "user_role": "admin"
            }
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@api_bp.route('/families/<family_id>/members', methods=['GET'])
@login_required
def get_family_members(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Convert family_id to UUID for validation, then to string for query
        try:
            uuid_obj = uuid.UUID(family_id)
            family_id_str = str(uuid_obj)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid family ID format"}), 400
        
        # First verify user is a member of this family
        cur.execute("""
            SELECT role FROM family_members
            WHERE family_id = %s AND user_id = %s AND is_active = true
        """, (family_id_str, current_user.id))
        
        user_role = cur.fetchone()
        if not user_role:
            return jsonify({"status": "error", "message": "Unauthorized access"}), 403
        
        # Get all members of the family
        cur.execute("""
            SELECT fm.id, fm.user_id, fm.role, fm.joined_at,
                u.email, u.first_name, u.last_name
            FROM family_members fm
            JOIN users u ON fm.user_id = u.id
            WHERE fm.family_id = %s AND fm.is_active = true
            ORDER BY fm.joined_at
        """, (family_id_str,))
        
        members = [
            {
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "role": row['role'],
                "joined_at": row['joined_at'].isoformat() if row['joined_at'] else None,
                "email": row['email'],
                "first_name": row['first_name'],
                "last_name": row['last_name']
            }
            for row in cur.fetchall()
        ]
        
        return jsonify(members)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

	
@api_bp.route('/recipes/<recipe_id>', methods=['GET'])
@api_bp.route('/recipes/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Validate UUID format but use string in query
        try:
            uuid_obj = uuid.UUID(recipe_id)
            recipe_id_str = str(uuid_obj)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid recipe ID format"}), 400
            
        # Get basic recipe info using the string representation
        cur.execute("""
            SELECT r.id, r.title, r.description, r.servings, r.prep_time_minutes, 
                r.cook_time_minutes, r.is_private, r.created_at, r.updated_at,
                c.name as cuisine_name, r.image_url
            FROM recipes r
            LEFT JOIN cuisines c ON r.cuisine_id = c.id
            WHERE r.id = %s
        """, (recipe_id_str,))
        
        recipe = cur.fetchone()
        
        if not recipe:
            return jsonify({"status": "error", "message": "Recipe not found"}), 404
        
        # Get ingredients using the same string representation
        cur.execute("""
            SELECT ri.quantity, bi.id as branded_ingredient_id, 
                bi.base_ingredient_id, b.id as brand_id, b.name as brand_name,
                i.name as ingredient_name, ri.display_order
            FROM recipe_ingredients ri
            JOIN branded_ingredients bi ON ri.branded_ingredient_id = bi.id
            JOIN base_ingredients i ON bi.base_ingredient_id = i.id
            LEFT JOIN brands b ON bi.brand_id = b.id
            WHERE ri.recipe_id = %s
            ORDER BY ri.display_order
        """, (recipe_id_str,))
        
        ingredients = []
        for row in cur.fetchall():
            ingredients.append({
                "id": str(row['branded_ingredient_id']),
                "name": row['ingredient_name'],
                "quantity": row['quantity'],
                "brand": row['brand_name']
            })
        
        # Get steps using the same string representation
        cur.execute("""
            SELECT step_number, description, media_url, media_type
            FROM recipe_steps
            WHERE recipe_id = %s
            ORDER BY step_number
        """, (recipe_id_str,))
        
        steps = []
        for row in cur.fetchall():
            steps.append({
                "step_number": row['step_number'],
                "description": row['description'],
                "media_url": row['media_url'],
                "media_type": row['media_type']
            })
        
        # Construct the full recipe object - always convert UUIDs to strings
        recipe_data = {
            "id": str(recipe['id']),
            "title": recipe['title'],
            "description": recipe['description'],
            "servings": recipe['servings'],
            "prep_time_minutes": recipe['prep_time_minutes'],
            "cook_time_minutes": recipe['cook_time_minutes'],
            "is_private": recipe['is_private'],
            "cuisine": recipe['cuisine_name'],
            "image_url": recipe['image_url'],
            "created_at": recipe['created_at'].isoformat() if recipe['created_at'] else None,
            "updated_at": recipe['updated_at'].isoformat() if recipe['updated_at'] else None,
            "ingredients": ingredients,
            "steps": steps
        }
        
        return jsonify(recipe_data)
    except Exception as e:
        print(f"Error fetching recipe: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@api_bp.route('/families/<family_id>/members/<member_id>', methods=['DELETE'])
@login_required
def remove_family_member(family_id, member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Convert IDs to UUIDs
        try:
            family_uuid = uuid.UUID(family_id)
            member_uuid = uuid.UUID(member_id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid ID format"}), 400
            
        # Verify current user is an admin of this family
        cur.execute("""
            SELECT role FROM family_members
            WHERE family_id = %s AND user_id = %s AND is_active = true
        """, (family_uuid, current_user.id))
        
        user_role = cur.fetchone()
        if not user_role or user_role['role'] != 'admin':
            # Allow users to remove themselves
            cur.execute("""
                SELECT user_id FROM family_members
                WHERE id = %s
            """, (member_uuid,))
            member_user_id = cur.fetchone()
            
            if not member_user_id or str(member_user_id['user_id']) != str(current_user.id):
                return jsonify({"status": "error", "message": "Only family admins can remove other members"}), 403
        
        # Check if the member exists and is part of this family
        cur.execute("""
            SELECT id FROM family_members
            WHERE id = %s AND family_id = %s
        """, (member_uuid, family_uuid))
        
        if not cur.fetchone():
            return jsonify({"status": "error", "message": "Member not found in this family"}), 404
        
        # Set the member as inactive (soft delete)
        cur.execute("""
            UPDATE family_members
            SET is_active = false
            WHERE id = %s
        """, (member_uuid,))
        
        conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Member removed successfully"
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@api_bp.route('/recipes/<recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Convert string ID to UUID for validation, then back to string for query
        try:
            uuid_obj = uuid.UUID(recipe_id)
            recipe_id_str = str(uuid_obj)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid recipe ID format"}), 400
            
        # Verify user owns this recipe
        cur.execute("""
            SELECT created_by_user_id FROM recipes
            WHERE id = %s
        """, (recipe_id_str,))
        
        recipe = cur.fetchone()
        if not recipe:
            return jsonify({"status": "error", "message": "Recipe not found"}), 404
            
        if str(recipe['created_by_user_id']) != str(current_user.id):
            return jsonify({"status": "error", "message": "You don't have permission to delete this recipe"}), 403
        
        # Delete recipe
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id_str,))
        cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (recipe_id_str,))
        cur.execute("DELETE FROM recipes WHERE id = %s", (recipe_id_str,))
        
        conn.commit()
        
        return jsonify({"status": "success", "message": "Recipe deleted successfully"})
    except Exception as e:
        conn.rollback()
        print(f"Error deleting recipe: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
		
		
# Main route
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp)  # Register API blueprint

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Create admin user before starting app
create_admin_user()

# For development
if __name__ == '__main__':
    app.run(debug=True)