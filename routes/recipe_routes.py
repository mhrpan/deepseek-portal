from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_utils import get_db_connection
import uuid

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipes', methods=['POST'])
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
@recipe_bp.route('/recipes/<recipe_id>', methods=['PUT'])
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

		
@recipe_bp.route('/user/recipes', methods=['GET'])
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
@recipe_bp.route('/recipes/<recipe_id>', methods=['GET'])
@recipe_bp.route('/recipes/<recipe_id>', methods=['GET'])
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


@recipe_bp.route('/recipes/<recipe_id>', methods=['DELETE'])
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