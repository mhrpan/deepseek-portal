import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from db_utils import admin_required, get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Context processor to inject stats into all admin templates
@admin_bp.context_processor
def inject_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    # Count users
    cur.execute("SELECT COUNT(*) FROM users")
    result = cur.fetchone()
    user_count = result['count'] if result else 0  # Change this line

    # Count recipes
    cur.execute("SELECT COUNT(*) FROM recipes")
    result = cur.fetchone()
    recipe_count = result['count'] if result else 0  # And this line

    # Count ingredients
    cur.execute("SELECT COUNT(*) FROM base_ingredients")
    result = cur.fetchone()
    ingredient_count = result['count'] if result else 0  # And this line

    # Count brands
    cur.execute("SELECT COUNT(*) FROM brands")
    result = cur.fetchone()
    brand_count = result['count'] if result else 0  # And this line

    # Count additives
    cur.execute("SELECT COUNT(*) FROM additives")
    result = cur.fetchone()
    additive_count = result['count'] if result else 0  # And this line

    # Count Branded Ingredients
    cur.execute("SELECT COUNT(*) FROM branded_ingredients")
    result = cur.fetchone()
    product_count = result['count'] if result else 0  # And this line

    cur.close()
    conn.close()

    stats = {
        'user_count': user_count,
        'recipe_count': recipe_count,
        'ingredient_count': ingredient_count,
        'brand_count': brand_count,
        'additive_count': additive_count,
        'product_count': product_count
    }
    return dict(stats=stats)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # With the context processor, stats is injected automatically.
    return render_template('admin/dashboard.html')

# Cuisines Management
@admin_bp.route('/cuisines')
@login_required
@admin_required
def cuisines():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get filter parameters
    name_filter = request.args.get('name', '')
    
    # Build query based on filters
    query = 'SELECT * FROM cuisines WHERE 1=1'
    params = []
    
    if name_filter:
        query += ' AND name ILIKE %s'
        params.append(f'%{name_filter}%')
    
    query += ' ORDER BY name'
    
    cur.execute(query, params)
    cuisines = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/cuisines/index.html', cuisines=cuisines)

@admin_bp.route('/cuisines/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cuisine():
    if request.method == 'POST':
        name = request.form.get('name')
        name_hindi = request.form.get('name_hindi', '')
        name_gujarati = request.form.get('name_gujarati', '')
        name_marathi = request.form.get('name_marathi', '')
        name_tamil = request.form.get('name_tamil', '')
        
        if not name:
            flash('Cuisine name is required', 'danger')
            return render_template('admin/cuisines/add.html')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                '''
                INSERT INTO cuisines (name, name_hindi, name_gujarati, name_marathi, name_tamil)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (name, name_hindi, name_gujarati, name_marathi, name_tamil)
            )
            conn.commit()
            flash('Cuisine added successfully', 'success')
            return redirect(url_for('admin.cuisines'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding cuisine: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/cuisines/add.html')

@admin_bp.route('/cuisines/edit/<uuid:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cuisine(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM cuisines WHERE id = %s', (str(id),))
    cuisine = cur.fetchone()
    
    if not cuisine:
        cur.close()
        conn.close()
        flash('Cuisine not found', 'danger')
        return redirect(url_for('admin.cuisines'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        name_hindi = request.form.get('name_hindi', '')
        name_gujarati = request.form.get('name_gujarati', '')
        name_marathi = request.form.get('name_marathi', '')
        name_tamil = request.form.get('name_tamil', '')
        
        if not name:
            flash('Cuisine name is required', 'danger')
            return render_template('admin/cuisines/edit.html', cuisine=cuisine)
        
        try:
            cur.execute(
                '''
                UPDATE cuisines 
                SET name = %s, name_hindi = %s, name_gujarati = %s, name_marathi = %s, name_tamil = %s
                WHERE id = %s
                ''',
                (name, name_hindi, name_gujarati, name_marathi, name_tamil, str(id))
            )
            conn.commit()
            flash('Cuisine updated successfully', 'success')
            return redirect(url_for('admin.cuisines'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating cuisine: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/cuisines/edit.html', cuisine=cuisine)

@admin_bp.route('/cuisines/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_cuisine(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the cuisine is being used in any recipes
        cur.execute('SELECT COUNT(*) FROM recipes WHERE cuisine_id = %s', (str(id),))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('Cannot delete cuisine as it is being used in recipes', 'danger')
            return redirect(url_for('admin.cuisines'))
        
        cur.execute('DELETE FROM cuisines WHERE id = %s', (str(id),))
        conn.commit()
        flash('Cuisine deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting cuisine: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.cuisines'))

# Base Ingredients Management
@admin_bp.route('/base-ingredients')
@login_required
@admin_required
def base_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all ingredients
    cur.execute('''
        SELECT bi.*, ic.name as category_name 
        FROM base_ingredients bi
        LEFT JOIN ingredient_categories ic ON bi.category_id = ic.id
        ORDER BY bi.name
    ''')
    ingredients = cur.fetchall()
    
    # Get all categories for the filter dropdown
    cur.execute('SELECT id, name FROM ingredient_categories ORDER BY name')
    categories = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/base_ingredients/index.html', 
                           ingredients=ingredients,
                           categories=categories)

@admin_bp.route('/base-ingredients/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_base_ingredient():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all categories for the dropdown
    cur.execute('SELECT * FROM ingredient_categories ORDER BY name')
    categories = cur.fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        name_hindi = request.form.get('name_hindi', '')
        name_gujarati = request.form.get('name_gujarati', '')
        name_marathi = request.form.get('name_marathi', '')
        name_tamil = request.form.get('name_tamil', '')
        category_id = request.form.get('category_id')
        is_verified = 'is_verified' in request.form
        
        if not name:
            flash('Ingredient name is required', 'danger')
            return render_template('admin/base_ingredients/add.html', categories=categories)
        
        # Check if ingredient already exists
        cur.execute('SELECT COUNT(*) FROM base_ingredients WHERE LOWER(name) = LOWER(%s)', (name,))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash(f'An ingredient with the name "{name}" already exists', 'danger')
            cur.close()
            conn.close()
            return render_template('admin/base_ingredients/add.html', categories=categories)
        
        try:
            cur.execute(
                '''
                INSERT INTO base_ingredients 
                (name, name_hindi, name_gujarati, name_marathi, name_tamil, category_id, is_verified, added_by_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    name, name_hindi, name_gujarati, name_marathi, name_tamil, 
                    category_id if category_id else None, 
                    is_verified,
                    current_user.id
                )
            )
            conn.commit()
            flash('Base ingredient added successfully', 'success')
            return redirect(url_for('admin.base_ingredients'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding base ingredient: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    else:
        cur.close()
        conn.close()
    
    return render_template('admin/base_ingredients/add.html', categories=categories)


@admin_bp.route('/base-ingredients/edit/<uuid:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_base_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM base_ingredients WHERE id = %s', (str(id),))
    ingredient = cur.fetchone()
    
    if not ingredient:
        cur.close()
        conn.close()
        flash('Ingredient not found', 'danger')
        return redirect(url_for('admin.base_ingredients'))
    
    # Get all categories for the dropdown
    cur.execute('SELECT * FROM ingredient_categories ORDER BY name')
    categories = cur.fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        name_hindi = request.form.get('name_hindi', '')
        name_gujarati = request.form.get('name_gujarati', '')
        name_marathi = request.form.get('name_marathi', '')
        name_tamil = request.form.get('name_tamil', '')
        category_id = request.form.get('category_id')
        is_verified = 'is_verified' in request.form
        
        if not name:
            flash('Ingredient name is required', 'danger')
            return render_template('admin/base_ingredients/edit.html', 
                                  ingredient=ingredient, 
                                  categories=categories)
        
        try:
            cur.execute(
                '''
                UPDATE base_ingredients 
                SET name = %s, name_hindi = %s, name_gujarati = %s, name_marathi = %s, 
                    name_tamil = %s, category_id = %s, is_verified = %s
                WHERE id = %s
                ''',
                (
                    name, name_hindi, name_gujarati, name_marathi, name_tamil, 
                    category_id if category_id else None, 
                    is_verified,
                    str(id)
                )
            )
            conn.commit()
            flash('Base ingredient updated successfully', 'success')
            return redirect(url_for('admin.base_ingredients'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating base ingredient: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    else:
        cur.close()
        conn.close()
    
    return render_template('admin/base_ingredients/edit.html', 
                          ingredient=ingredient, 
                          categories=categories)

@admin_bp.route('/base-ingredients/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_base_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the ingredient is being used in any branded ingredients
        cur.execute('SELECT COUNT(*) FROM branded_ingredients WHERE base_ingredient_id = %s', (str(id),))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('Cannot delete ingredient as it is being used in branded ingredients', 'danger')
            return redirect(url_for('admin.base_ingredients'))
        
        cur.execute('DELETE FROM base_ingredients WHERE id = %s', (str(id),))
        conn.commit()
        flash('Base ingredient deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting base ingredient: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.base_ingredients'))

# Brands Management
@admin_bp.route('/brands')
@login_required
@admin_required
def brands():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM brands ORDER BY name')
    brands = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/brands/index.html', brands=brands)

@admin_bp.route('/brands/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_brand():
    if request.method == 'POST':
        name = request.form.get('name')
        is_verified = 'is_verified' in request.form
        
        if not name:
            flash('Brand name is required', 'danger')
            return render_template('admin/brands/add.html')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if brand already exists
        cur.execute('SELECT COUNT(*) FROM brands WHERE LOWER(name) = LOWER(%s)', (name,))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash(f'A brand with the name "{name}" already exists', 'danger')
            cur.close()
            conn.close()
            return render_template('admin/brands/add.html')
        
        try:
            cur.execute(
                '''
                INSERT INTO brands (name, is_verified, added_by_user_id)
                VALUES (%s, %s, %s)
                ''',
                (name, is_verified, current_user.id)
            )
            conn.commit()
            flash('Brand added successfully', 'success')
            return redirect(url_for('admin.brands'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding brand: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/brands/add.html')

@admin_bp.route('/brands/edit/<uuid:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_brand(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM brands WHERE id = %s', (str(id),))
    brand = cur.fetchone()
    
    if not brand:
        cur.close()
        conn.close()
        flash('Brand not found', 'danger')
        return redirect(url_for('admin.brands'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        is_verified = 'is_verified' in request.form
        
        if not name:
            flash('Brand name is required', 'danger')
            return render_template('admin/brands/edit.html', brand=brand)
        
        try:
            cur.execute(
                '''
                UPDATE brands 
                SET name = %s, is_verified = %s
                WHERE id = %s
                ''',
                (name, is_verified, str(id))
            )
            conn.commit()
            flash('Brand updated successfully', 'success')
            return redirect(url_for('admin.brands'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating brand: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/brands/edit.html', brand=brand)

@admin_bp.route('/brands/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_brand(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the brand is being used in any branded ingredients
        cur.execute('SELECT COUNT(*) FROM branded_ingredients WHERE brand_id = %s', (str(id),))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('Cannot delete brand as it is being used in branded ingredients', 'danger')
            return redirect(url_for('admin.brands'))
        
        cur.execute('DELETE FROM brands WHERE id = %s', (str(id),))
        conn.commit()
        flash('Brand deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting brand: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.brands'))

# Branded Ingredients Management
@admin_bp.route('/branded-ingredients')
@login_required
@admin_required
def branded_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get branded ingredients
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name, 
               bi.description, bi.is_verified, bi.created_at, bi.image_url
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        ORDER BY b.name, i.name
    ''')
    branded_ingredients = cur.fetchall()
    
    # Get all brands for filter dropdown
    cur.execute('SELECT id, name FROM brands ORDER BY name')
    brands = cur.fetchall()
    
    # Get all base ingredients for filter dropdown
    cur.execute('SELECT id, name FROM base_ingredients ORDER BY name')
    base_ingredients = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/index.html', 
                          branded_ingredients=branded_ingredients,
                          brands=brands,
                          base_ingredients=base_ingredients)

@admin_bp.route('/branded-ingredients/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_branded_ingredient():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all base ingredients and brands for dropdowns
    cur.execute('SELECT id, name FROM base_ingredients ORDER BY name')
    base_ingredients = cur.fetchall()
    
    cur.execute('SELECT id, name FROM brands ORDER BY name')
    brands = cur.fetchall()
    
    if request.method == 'POST':
        base_ingredient_id = request.form.get('base_ingredient_id')
        brand_id = request.form.get('brand_id')
        description = request.form.get('description', '')
        is_verified = 'is_verified' in request.form
        
        if not base_ingredient_id or not brand_id:
            flash('Base ingredient and brand are required', 'danger')
            return render_template('admin/branded_ingredients/add.html', 
                                  base_ingredients=base_ingredients,
                                  brands=brands)
        
        # Check if combination already exists
        cur.execute(
            'SELECT COUNT(*) FROM branded_ingredients WHERE base_ingredient_id = %s AND brand_id = %s',
            (base_ingredient_id, brand_id)
        )
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('This branded ingredient combination already exists', 'danger')
            return render_template('admin/branded_ingredients/add.html', 
                                  base_ingredients=base_ingredients,
                                  brands=brands)
        
        # Handle image upload if provided
        image_url = None
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            filename = secure_filename(image.filename)
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            # Save to upload folder - make sure this directory exists
            upload_path = os.path.join('static', 'uploads', 'ingredients')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, unique_filename)
            image.save(file_path)
            image_url = f"/static/uploads/ingredients/{unique_filename}"
        
        try:
            cur.execute(
                '''
                INSERT INTO branded_ingredients 
                (base_ingredient_id, brand_id, description, image_url, is_verified, added_by_user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                (base_ingredient_id, brand_id, description, image_url, is_verified, current_user.id)
            )
            conn.commit()
            flash('Branded ingredient added successfully', 'success')
            return redirect(url_for('admin.branded_ingredients'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding branded ingredient: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    else:
        cur.close()
        conn.close()
    
    return render_template('admin/branded_ingredients/add.html', 
                          base_ingredients=base_ingredients,
                          brands=brands)

@admin_bp.route('/branded-ingredients/edit/<uuid:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_branded_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT bi.*, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    branded_ingredient = cur.fetchone()
    
    if not branded_ingredient:
        cur.close()
        conn.close()
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    if request.method == 'POST':
        description = request.form.get('description', '')
        is_verified = 'is_verified' in request.form
        
        # Handle image upload if provided
        image_url = branded_ingredient['image_url']
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            filename = secure_filename(image.filename)
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            # Save to upload folder
            upload_path = os.path.join('static', 'uploads', 'ingredients')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, unique_filename)
            image.save(file_path)
            
            # Remove old image if exists
            if image_url and os.path.exists(os.path.join('static', image_url.lstrip('/'))):
                os.remove(os.path.join('static', image_url.lstrip('/')))
            
            image_url = f"/static/uploads/ingredients/{unique_filename}"
        
        try:
            cur.execute(
                '''
                UPDATE branded_ingredients 
                SET description = %s, image_url = %s, is_verified = %s
                WHERE id = %s
                ''',
                (description, image_url, is_verified, str(id))
            )
            conn.commit()
            flash('Branded ingredient updated successfully', 'success')
            return redirect(url_for('admin.branded_ingredients'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating branded ingredient: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/edit.html', 
                          branded_ingredient=branded_ingredient)

@admin_bp.route('/branded-ingredients/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_branded_ingredient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the branded ingredient is being used in any recipes
        cur.execute('SELECT COUNT(*) FROM recipe_ingredients WHERE branded_ingredient_id = %s', (str(id),))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('Cannot delete branded ingredient as it is being used in recipes', 'danger')
            return redirect(url_for('admin.branded_ingredients'))
        
        # Get image URL to delete file if exists
        cur.execute('SELECT image_url FROM branded_ingredients WHERE id = %s', (str(id),))
        result = cur.fetchone()
        
        if result and result['image_url'] and os.path.exists(os.path.join('static', result['image_url'].lstrip('/'))):
            os.remove(os.path.join('static', result['image_url'].lstrip('/')))
        
        cur.execute('DELETE FROM branded_ingredients WHERE id = %s', (str(id),))
        conn.commit()
        flash('Branded ingredient deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting branded ingredient: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.branded_ingredients'))

	
# Additive Categories Management
@admin_bp.route('/additive-categories')
@login_required
@admin_required
def additive_categories():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM additive_categories ORDER BY name')
    categories = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/additive_categories/index.html', categories=categories)

@admin_bp.route('/additive-categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_additive_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        name_hindi = request.form.get('name_hindi', '')
        name_gujarati = request.form.get('name_gujarati', '')
        name_marathi = request.form.get('name_marathi', '')
        name_tamil = request.form.get('name_tamil', '')
        
        if not name:
            flash('Category name is required', 'danger')
            return render_template('admin/additive_categories/add.html')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                '''
                INSERT INTO additive_categories
                (name, description, name_hindi, name_gujarati, name_marathi, name_tamil)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                (name, description, name_hindi, name_gujarati, name_marathi, name_tamil)
            )
            conn.commit()
            flash('Additive category added successfully', 'success')
            return redirect(url_for('admin.additive_categories'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding additive category: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/additive_categories/add.html')

# Additives Management
@admin_bp.route('/additives')
@login_required
@admin_required
def additives():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get filter parameters
    category_id = request.args.get('category_id')
    is_natural = request.args.get('is_natural')
    is_verified = request.args.get('is_verified')
    search = request.args.get('search', '')
    
    # Get all additive categories for filter
    cur.execute('SELECT * FROM additive_categories ORDER BY name')
    categories = cur.fetchall()
    
    # Build query with filters
    query = '''
        SELECT a.*, ac.name as category_name
        FROM additives a
        LEFT JOIN additive_categories ac ON a.category_id = ac.id
        WHERE 1=1
    '''
    params = []
    
    if search:
        query += " AND (a.name ILIKE %s OR a.code ILIKE %s)"
        search_pattern = f'%{search}%'
        params.extend([search_pattern, search_pattern])
    
    if category_id:
        query += " AND a.category_id = %s"
        params.append(category_id)
    
    if is_natural:
        is_natural_bool = is_natural.lower() == 'true'
        query += " AND a.is_natural = %s"
        params.append(is_natural_bool)
    
    if is_verified:
        is_verified_bool = is_verified.lower() == 'true'
        query += " AND a.is_verified = %s"
        params.append(is_verified_bool)
    
    query += " ORDER BY a.code, a.name"
    
    cur.execute(query, params)
    additives_list = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/additives/index.html', 
                          additives=additives_list,
                          categories=categories)

@admin_bp.route('/additives/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_additive():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all categories for the dropdown
    cur.execute('SELECT * FROM additive_categories ORDER BY name')
    categories = cur.fetchall()
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        description = request.form.get('description', '')
        health_implications = request.form.get('health_implications', '')
        is_natural = 'is_natural' in request.form
        is_vegan = 'is_vegan' in request.form
        is_verified = 'is_verified' in request.form
        
        if not code or not name:
            flash('Code and name are required', 'danger')
            return render_template('admin/additives/add.html', categories=categories)
        
        # Check if additive code already exists (case-insensitive)
        cur.execute('SELECT COUNT(*) FROM additives WHERE LOWER(code) = LOWER(%s)', (code,))
        if cur.fetchone()[0] > 0:
            flash(f'An additive with code {code} already exists', 'danger')
            return render_template('admin/additives/add.html', categories=categories)
        
        try:
            cur.execute(
                '''
                INSERT INTO additives
                (code, name, category_id, description, health_implications, is_natural, is_vegan, is_verified, added_by_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (code, name, category_id, description, health_implications, 
                 is_natural, is_vegan, is_verified, current_user.id)
            )
            conn.commit()
            flash('Additive added successfully', 'success')
            return redirect(url_for('admin.additives'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding additive: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    else:
        cur.close()
        conn.close()
    
    return render_template('admin/additives/add.html', categories=categories)

@admin_bp.route('/additives/edit/<uuid:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_additive(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM additives WHERE id = %s', (str(id),))
    additive = cur.fetchone()
    
    if not additive:
        cur.close()
        conn.close()
        flash('Additive not found', 'danger')
        return redirect(url_for('admin.additives'))
    
    # Get all categories for the dropdown
    cur.execute('SELECT * FROM additive_categories ORDER BY name')
    categories = cur.fetchall()
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        description = request.form.get('description', '')
        health_implications = request.form.get('health_implications', '')
        is_natural = 'is_natural' in request.form
        is_vegan = 'is_vegan' in request.form
        is_verified = 'is_verified' in request.form
        
        if not code or not name:
            flash('Code and name are required', 'danger')
            return render_template('admin/additives/edit.html', 
                                 additive=additive, 
                                 categories=categories)
        
        # Check if another additive already has this code
        cur.execute('SELECT COUNT(*) FROM additives WHERE code = %s AND id != %s', (code, str(id)))
        if cur.fetchone()[0] > 0:
            flash(f'Another additive with code {code} already exists', 'danger')
            return render_template('admin/additives/edit.html', 
                                 additive=additive, 
                                 categories=categories)
        
        try:
            cur.execute(
                '''
                UPDATE additives
                SET code = %s, name = %s, category_id = %s, description = %s,
                    health_implications = %s, is_natural = %s, is_vegan = %s, is_verified = %s
                WHERE id = %s
                ''',
                (code, name, category_id, description, health_implications, 
                 is_natural, is_vegan, is_verified, str(id))
            )
            conn.commit()
            flash('Additive updated successfully', 'success')
            return redirect(url_for('admin.additives'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating additive: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    else:
        cur.close()
        conn.close()
    
    return render_template('admin/additives/edit.html', 
                         additive=additive, 
                         categories=categories)

@admin_bp.route('/additives/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_additive(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the additive is being used in any products
        cur.execute('SELECT COUNT(*) FROM product_additives WHERE additive_id = %s', (str(id),))
        count = cur.fetchone()[0]
        
        if count > 0:
            flash('Cannot delete additive as it is being used in products', 'danger')
            return redirect(url_for('admin.additives'))
        
        cur.execute('DELETE FROM additives WHERE id = %s', (str(id),))
        conn.commit()
        flash('Additive deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting additive: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.additives'))
	
	
# Product Images Management
@admin_bp.route('/branded-ingredients/<uuid:id>/images')
@login_required
@admin_required
def manage_product_images(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the branded ingredient details
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    if not product:
        cur.close()
        conn.close()
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    # Get all images for this product
    cur.execute('''
        SELECT * FROM product_images
        WHERE branded_ingredient_id = %s
        ORDER BY is_primary DESC, created_at DESC
    ''', (str(id),))
    product_images = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/manage_images.html', 
                          product=product,
                          product_images=product_images)

@admin_bp.route('/branded-ingredients/<uuid:id>/images/add', methods=['POST'])
@login_required
@admin_required
def add_product_image(id):
    if 'image' not in request.files or not request.files['image'].filename:
        flash('No image selected', 'danger')
        return redirect(url_for('admin.manage_product_images', id=id))
    
    image = request.files['image']
    image_type = request.form.get('image_type', 'other')
    is_primary = 'is_primary' in request.form
    
    # Save the image
    filename = secure_filename(image.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    upload_path = os.path.join('static', 'uploads', 'products')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    image.save(file_path)
    image_url = f"/static/uploads/products/{unique_filename}"
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # If setting as primary, update any existing primary images
        if is_primary:
            cur.execute('''
                UPDATE product_images
                SET is_primary = FALSE
                WHERE branded_ingredient_id = %s
            ''', (str(id),))
        
        # Insert the new image
        cur.execute('''
            INSERT INTO product_images
            (branded_ingredient_id, image_url, image_type, is_primary)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (str(id), image_url, image_type, is_primary))
        
        image_id = cur.fetchone()[0]
        conn.commit()
        flash('Image added successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding image: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_images', id=id))

@admin_bp.route('/product-images/<uuid:image_id>/set-primary', methods=['POST'])
@login_required
@admin_required
def set_primary_image(image_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the branded ingredient ID from the image
        cur.execute('SELECT branded_ingredient_id FROM product_images WHERE id = %s', (str(image_id),))
        result = cur.fetchone()
        if not result:
            raise Exception('Image not found')
        
        branded_ingredient_id = result['branded_ingredient_id']
        
        # Update all images for this product to not be primary
        cur.execute('''
            UPDATE product_images
            SET is_primary = FALSE
            WHERE branded_ingredient_id = %s
        ''', (branded_ingredient_id,))
        
        # Set this image as primary
        cur.execute('''
            UPDATE product_images
            SET is_primary = TRUE
            WHERE id = %s
        ''', (str(image_id),))
        
        conn.commit()
        flash('Primary image updated successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating primary image: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_images', id=branded_ingredient_id))

@admin_bp.route('/product-images/<uuid:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product_image(image_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the image details
        cur.execute('SELECT branded_ingredient_id, image_url, is_primary FROM product_images WHERE id = %s', (str(image_id),))
        result = cur.fetchone()
        if not result:
            raise Exception('Image not found')
        
        branded_ingredient_id = result['branded_ingredient_id']
        image_url = result['image_url']
        was_primary = result['is_primary']
        
        # Delete the image from the database
        cur.execute('DELETE FROM product_images WHERE id = %s', (str(image_id),))
        
        # If this was the primary image, set another image as primary if available
        if was_primary:
            cur.execute('''
                UPDATE product_images
                SET is_primary = TRUE
                WHERE branded_ingredient_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            ''', (branded_ingredient_id,))
        
        conn.commit()
        
        # Delete the file from disk
        if image_url and os.path.exists(os.path.join('static', image_url.lstrip('/'))):
            os.remove(os.path.join('static', image_url.lstrip('/')))
        
        flash('Image deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting image: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_images', id=branded_ingredient_id))

@admin_bp.route('/product-images/<uuid:image_id>/extract-text')
@login_required
@admin_required
def extract_image_text(image_id):
    import pytesseract
    from PIL import Image
    import os
    
    # Set the Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the image details
        cur.execute('SELECT branded_ingredient_id, image_url FROM product_images WHERE id = %s', (str(image_id),))
        result = cur.fetchone()
        if not result:
            raise Exception('Image not found in database')
        
        branded_ingredient_id = result['branded_ingredient_id']
        image_url = result['image_url']
        
        # Print debug info
        print(f"Image URL from database: {image_url}")
        
        # Try different path approaches
        possible_paths = [
            os.path.join('static', image_url.lstrip('/')),  # Relative to project root
            os.path.join(os.getcwd(), 'static', image_url.lstrip('/')),  # Absolute path
            image_url.lstrip('/'),  # Just the path part
            os.path.abspath(os.path.join('static', image_url.lstrip('/')))  # Absolute normalized path
        ]
        
        # Try to find the file
        image_path = None
        for path in possible_paths:
            print(f"Trying path: {path}")
            if os.path.exists(path):
                image_path = path
                print(f"Found image at: {image_path}")
                break
        
        if not image_path:
            raise Exception(f'Image file not found on disk. Tried paths: {possible_paths}')
        
        # Use Tesseract to extract text
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        
        print(f"Extracted text: {extracted_text[:100]}...")  # Print first 100 chars
        
        # Update the image with the extracted text
        cur.execute('''
            UPDATE product_images
            SET extracted_text = %s
            WHERE id = %s
        ''', (extracted_text, str(image_id)))
        
        conn.commit()
        flash('Text extracted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error extracting text: {str(e)}', 'danger')
        print(f"Error in OCR processing: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_images', id=branded_ingredient_id))

# Product Additives Management
@admin_bp.route('/branded-ingredients/<uuid:id>/additives')
@login_required
@admin_required
def manage_product_additives(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the branded ingredient details
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    if not product:
        cur.close()
        conn.close()
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    # Get all additives for this product
    cur.execute('''
        SELECT a.*, ac.name as category_name
        FROM additives a
        JOIN product_additives pa ON a.id = pa.additive_id
        LEFT JOIN additive_categories ac ON a.category_id = ac.id
        WHERE pa.branded_ingredient_id = %s
        ORDER BY a.code
    ''', (str(id),))
    product_additives = cur.fetchall()
    
    # Get all available additives not already added to this product
    cur.execute('''
        SELECT a.* 
        FROM additives a
        WHERE a.id NOT IN (
            SELECT additive_id 
            FROM product_additives 
            WHERE branded_ingredient_id = %s
        )
        ORDER BY a.code
    ''', (str(id),))
    available_additives = cur.fetchall()
    
    # Get ingredient list if exists
    cur.execute('SELECT * FROM ingredient_lists WHERE branded_ingredient_id = %s', (str(id),))
    ingredient_list = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/manage_additives.html', 
                          product=product,
                          product_additives=product_additives,
                          available_additives=available_additives,
                          ingredient_list=ingredient_list)

@admin_bp.route('/branded-ingredients/<uuid:id>/additives/add', methods=['POST'])
@login_required
@admin_required
def add_product_additive(id):
    additive_id = request.form.get('additive_id')
    
    if not additive_id:
        flash('No additive selected', 'danger')
        return redirect(url_for('admin.manage_product_additives', id=id))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if already exists
        cur.execute('''
            SELECT COUNT(*) FROM product_additives
            WHERE branded_ingredient_id = %s AND additive_id = %s
        ''', (str(id), additive_id))
        
        if cur.fetchone()[0] > 0:
            flash('This additive is already added to the product', 'warning')
            return redirect(url_for('admin.manage_product_additives', id=id))
        
        # Add the additive
        cur.execute('''
            INSERT INTO product_additives (branded_ingredient_id, additive_id)
            VALUES (%s, %s)
        ''', (str(id), additive_id))
        
        conn.commit()
        flash('Additive added successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding additive: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_additives', id=id))

@admin_bp.route('/branded-ingredients/<uuid:id>/additives/remove/<uuid:additive_id>', methods=['POST'])
@login_required
@admin_required
def remove_product_additive(id, additive_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            DELETE FROM product_additives
            WHERE branded_ingredient_id = %s AND additive_id = %s
        ''', (str(id), str(additive_id)))
        
        conn.commit()
        flash('Additive removed successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error removing additive: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_additives', id=id))

@admin_bp.route('/branded-ingredients/<uuid:id>/ingredient-list/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_ingredient_list(id):
    if request.method == 'POST':
        ingredients_text = request.form.get('ingredients_text')
        is_verified = 'is_verified' in request.form
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('''
                INSERT INTO ingredient_lists 
                (branded_ingredient_id, ingredients_text, is_verified)
                VALUES (%s, %s, %s)
            ''', (str(id), ingredients_text, is_verified))
            
            conn.commit()
            flash('Ingredient list added successfully', 'success')
            return redirect(url_for('admin.manage_product_additives', id=id))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding ingredient list: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()

    # Get the branded ingredient details for the form
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not product:
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    return render_template('admin/branded_ingredients/add_ingredient_list.html', product=product)

@admin_bp.route('/branded-ingredients/<uuid:id>/ingredient-list/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ingredient_list(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the current ingredient list
    cur.execute('SELECT * FROM ingredient_lists WHERE branded_ingredient_id = %s', (str(id),))
    ingredient_list = cur.fetchone()
    
    if not ingredient_list:
        cur.close()
        conn.close()
        flash('Ingredient list not found', 'danger')
        return redirect(url_for('admin.manage_product_additives', id=id))
    
    # Get the branded ingredient details
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    if request.method == 'POST':
        ingredients_text = request.form.get('ingredients_text')
        is_verified = 'is_verified' in request.form
        
        try:
            cur.execute('''
                UPDATE ingredient_lists
                SET ingredients_text = %s, is_verified = %s
                WHERE branded_ingredient_id = %s
            ''', (ingredients_text, is_verified, str(id)))
            
            conn.commit()
            flash('Ingredient list updated successfully', 'success')
            return redirect(url_for('admin.manage_product_additives', id=id))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating ingredient list: {str(e)}', 'danger')
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/edit_ingredient_list.html', 
                          product=product,
                          ingredient_list=ingredient_list)

# Nutritional Information Management
@admin_bp.route('/branded-ingredients/<uuid:id>/nutrients')
@login_required
@admin_required
def manage_product_nutrients(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the branded ingredient details
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    if not product:
        cur.close()
        conn.close()
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    # Get serving information
    cur.execute('SELECT * FROM serving_info WHERE branded_ingredient_id = %s', (str(id),))
    serving_info = cur.fetchone()
    
    # Get all nutrients for this product
    cur.execute('''
        SELECT pn.id, pn.amount, pn.percent_daily_value, pn.per_serving,
               n.name as nutrient_name, n.unit, nc.name as category_name
        FROM product_nutrients pn
        JOIN nutrients n ON pn.nutrient_id = n.id
        LEFT JOIN nutrient_categories nc ON n.category_id = nc.id
        WHERE pn.branded_ingredient_id = %s
        ORDER BY nc.display_order, n.display_order
    ''', (str(id),))
    product_nutrients = cur.fetchall()
    
    # Get all available nutrients not already added to this product
    cur.execute('''
        SELECT n.* 
        FROM nutrients n
        WHERE n.id NOT IN (
            SELECT nutrient_id 
            FROM product_nutrients 
            WHERE branded_ingredient_id = %s
        )
        ORDER BY n.name
    ''', (str(id),))
    available_nutrients = cur.fetchall()
    
    # Get all nutrient categories
    cur.execute('SELECT * FROM nutrient_categories ORDER BY display_order')
    nutrient_categories = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/manage_nutrients.html', 
                          product=product,
                          serving_info=serving_info,
                          product_nutrients=product_nutrients,
                          available_nutrients=available_nutrients,
                          nutrient_categories=nutrient_categories)

@admin_bp.route('/branded-ingredients/<uuid:id>/nutrients/add', methods=['POST'])
@login_required
@admin_required
def add_product_nutrient(id):
    nutrient_id = request.form.get('nutrient_id')
    amount = request.form.get('amount')
    percent_daily_value = request.form.get('percent_daily_value')
    per_serving = request.form.get('per_serving') == 'true'
    
    if not nutrient_id or not amount:
        flash('Nutrient and amount are required', 'danger')
        return redirect(url_for('admin.manage_product_nutrients', id=id))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if already exists
        cur.execute('''
            SELECT COUNT(*) FROM product_nutrients
            WHERE branded_ingredient_id = %s AND nutrient_id = %s
        ''', (str(id), nutrient_id))
        
        if cur.fetchone()[0] > 0:
            flash('This nutrient is already added to the product', 'warning')
            return redirect(url_for('admin.manage_product_nutrients', id=id))
        
        # Add the nutrient
        cur.execute('''
            INSERT INTO product_nutrients 
            (branded_ingredient_id, nutrient_id, amount, percent_daily_value, per_serving)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            str(id), 
            nutrient_id, 
            amount, 
            percent_daily_value if percent_daily_value else None, 
            per_serving
        ))
        
        conn.commit()
        flash('Nutrient added successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding nutrient: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_nutrients', id=id))

@admin_bp.route('/branded-ingredients/<uuid:id>/nutrients/edit', methods=['POST'])
@login_required
@admin_required
def edit_product_nutrient(id):
    nutrient_id = request.form.get('nutrient_id')
    amount = request.form.get('amount')
    percent_daily_value = request.form.get('percent_daily_value')
    per_serving = request.form.get('per_serving') == 'true'
    
    if not nutrient_id or not amount:
        flash('Nutrient and amount are required', 'danger')
        return redirect(url_for('admin.manage_product_nutrients', id=id))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            UPDATE product_nutrients
            SET amount = %s, percent_daily_value = %s, per_serving = %s
            WHERE id = %s AND branded_ingredient_id = %s
        ''', (
            amount,
            percent_daily_value if percent_daily_value else None,
            per_serving,
            nutrient_id,
            str(id)
        ))
        
        conn.commit()
        flash('Nutrient updated successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating nutrient: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_nutrients', id=id))

@admin_bp.route('/branded-ingredients/<uuid:id>/nutrients/delete/<uuid:nutrient_id>', methods=['POST'])
@login_required
@admin_required
def delete_product_nutrient(id, nutrient_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            DELETE FROM product_nutrients
            WHERE id = %s AND branded_ingredient_id = %s
        ''', (str(nutrient_id), str(id)))
        
        conn.commit()
        flash('Nutrient removed successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error removing nutrient: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.manage_product_nutrients', id=id))

@admin_bp.route('/branded-ingredients/<uuid:id>/serving-info/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_serving_info(id):
    if request.method == 'POST':
        serving_size = request.form.get('serving_size')
        serving_unit = request.form.get('serving_unit')
        servings_per_container = request.form.get('servings_per_container')
        
        if not serving_size or not serving_unit:
            flash('Serving size and unit are required', 'danger')
            return redirect(url_for('admin.add_serving_info', id=id))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('''
                INSERT INTO serving_info 
                (branded_ingredient_id, serving_size, serving_unit, servings_per_container)
                VALUES (%s, %s, %s, %s)
            ''', (
                str(id),
                serving_size,
                serving_unit,
                servings_per_container if servings_per_container else None
            ))
            
            conn.commit()
            flash('Serving information added successfully', 'success')
            return redirect(url_for('admin.manage_product_nutrients', id=id))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding serving information: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()
    
    # Get the branded ingredient details for the form
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not product:
        flash('Branded ingredient not found', 'danger')
        return redirect(url_for('admin.branded_ingredients'))
    
    return render_template('admin/branded_ingredients/add_serving_info.html', product=product)

@admin_bp.route('/branded-ingredients/<uuid:id>/serving-info/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_serving_info(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the current serving info
    cur.execute('SELECT * FROM serving_info WHERE branded_ingredient_id = %s', (str(id),))
    serving_info = cur.fetchone()
    
    if not serving_info:
        cur.close()
        conn.close()
        flash('Serving information not found', 'danger')
        return redirect(url_for('admin.manage_product_nutrients', id=id))
    
    # Get the branded ingredient details
    cur.execute('''
        SELECT bi.id, b.name as brand_name, i.name as ingredient_name
        FROM branded_ingredients bi
        JOIN brands b ON bi.brand_id = b.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        WHERE bi.id = %s
    ''', (str(id),))
    product = cur.fetchone()
    
    if request.method == 'POST':
        serving_size = request.form.get('serving_size')
        serving_unit = request.form.get('serving_unit')
        servings_per_container = request.form.get('servings_per_container')
        
        if not serving_size or not serving_unit:
            flash('Serving size and unit are required', 'danger')
            return render_template('admin/branded_ingredients/edit_serving_info.html',
                                 product=product,
                                 serving_info=serving_info)
        
        try:
            cur.execute('''
                UPDATE serving_info
                SET serving_size = %s, serving_unit = %s, servings_per_container = %s
                WHERE branded_ingredient_id = %s
            ''', (
                serving_size,
                serving_unit,
                servings_per_container if servings_per_container else None,
                str(id)
            ))
            
            conn.commit()
            flash('Serving information updated successfully', 'success')
            return redirect(url_for('admin.manage_product_nutrients', id=id))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating serving information: {str(e)}', 'danger')
    
    cur.close()
    conn.close()
    
    return render_template('admin/branded_ingredients/edit_serving_info.html',
                          product=product,
                          serving_info=serving_info)
						  

# Add these routes to your admin.py file

@admin_bp.route('/recipes')
@login_required
@admin_required
def recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get filter parameters
    title_filter = request.args.get('title', '')
    cuisine_id = request.args.get('cuisine_id')
    user_id = request.args.get('user_id')
    
    # Build query based on filters
    query = '''
        SELECT r.id, r.title, r.description, r.servings, r.prep_time_minutes, 
            r.cook_time_minutes, r.created_at, r.updated_at, r.is_private,
            u.first_name || ' ' || u.last_name AS creator_name,
            c.name AS cuisine_name
        FROM recipes r
        JOIN users u ON r.created_by_user_id = u.id
        LEFT JOIN cuisines c ON r.cuisine_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if title_filter:
        query += " AND r.title ILIKE %s"
        params.append(f'%{title_filter}%')
    
    if cuisine_id:
        query += " AND r.cuisine_id = %s"
        params.append(cuisine_id)
    
    if user_id:
        query += " AND r.created_by_user_id = %s"
        params.append(user_id)
    
    query += " ORDER BY r.created_at DESC"
    
    cur.execute(query, params)
    recipes_list = cur.fetchall()
    
    # Get all cuisines for filter dropdown
    cur.execute('SELECT id, name FROM cuisines ORDER BY name')
    cuisines = cur.fetchall()
    
    # Get all users for filter dropdown
    cur.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/recipes/index.html', 
                          recipes=recipes_list,
                          cuisines=cuisines,
                          users=users)

# Update your view_recipe function in admin.py to add more logging and debugging

@admin_bp.route('/recipes/<uuid:id>')
@login_required
@admin_required
def view_recipe(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get recipe details
    cur.execute('''
        SELECT r.*, 
            u.first_name || ' ' || u.last_name AS creator_name,
            c.name AS cuisine_name
        FROM recipes r
        JOIN users u ON r.created_by_user_id = u.id
        LEFT JOIN cuisines c ON r.cuisine_id = c.id
        WHERE r.id = %s
    ''', (str(id),))
    
    recipe = cur.fetchone()
    
    if not recipe:
        cur.close()
        conn.close()
        flash('Recipe not found', 'danger')
        return redirect(url_for('admin.recipes'))
    
    # Log the image URL for debugging
    print(f"Recipe image URL: {recipe.get('image_url')}")
    
    # Get ingredients
    cur.execute('''
        SELECT ri.id, ri.quantity, ri.notes,
            bi.id as branded_ingredient_id,
            b.name as brand_name,
            i.name as ingredient_name
        FROM recipe_ingredients ri
        JOIN branded_ingredients bi ON ri.branded_ingredient_id = bi.id
        JOIN base_ingredients i ON bi.base_ingredient_id = i.id
        JOIN brands b ON bi.brand_id = b.id
        WHERE ri.recipe_id = %s
        ORDER BY ri.display_order
    ''', (str(id),))
    
    ingredients = cur.fetchall()
    
    # Get steps
    cur.execute('''
        SELECT * 
        FROM recipe_steps
        WHERE recipe_id = %s
        ORDER BY step_number
    ''', (str(id),))
    
    steps = cur.fetchall()
    
    # Log step media URLs for debugging
    for step in steps:
        if step.get('media_url'):
            print(f"Step {step.get('step_number')} media URL: {step.get('media_url')}")
    
    cur.close()
    conn.close()
    
    return render_template('admin/recipes/view.html', 
                          recipe=recipe,
                          ingredients=ingredients,
                          steps=steps)

@admin_bp.route('/recipes/delete/<uuid:id>', methods=['POST'])
@login_required
@admin_required
def delete_recipe(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Delete recipe and all related data
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (str(id),))
        cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (str(id),))
        cur.execute("DELETE FROM recipe_tags WHERE recipe_id = %s", (str(id),))
        cur.execute("DELETE FROM recipe_sharing WHERE recipe_id = %s", (str(id),))
        cur.execute("DELETE FROM recipe_media WHERE recipe_id = %s", (str(id),))
        cur.execute("DELETE FROM recipes WHERE id = %s", (str(id),))
        
        conn.commit()
        flash('Recipe deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting recipe: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin.recipes'))