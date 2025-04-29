from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_utils import get_db_connection
import uuid

family_bp = Blueprint('family', __name__)

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