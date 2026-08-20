from flask import Blueprint, request, jsonify
from src.domain.services.search_engine import SmartSearchEngine
from src.infrastructure.security.decorators import login_required
from src.infrastructure.security.rate_limiter import rate_limit
from src.infrastructure.cache.cache_service import cache_response

search_api = Blueprint('search_api', __name__)

@search_api.route('/api/v2/search', methods=['GET'])
@login_required
@rate_limit('search')
@cache_response(ttl_seconds=15)
def smart_search():
    """API endpoint evaluating NLP patterns and keywords for smart search registries."""
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'desc')
    category = request.args.get('category')
    trust_level = request.args.get('trust_level')
    
    result = SmartSearchEngine.execute_search(
        query=query,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
        category=category,
        trust_level=trust_level
    )
    return jsonify(result), 200

@search_api.route('/api/v2/search/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    """API endpoint returning search suggestions and dynamic prefix completion lists."""
    prefix = request.args.get('prefix', '')
    if not prefix:
        return jsonify({'success': True, 'suggestions': []}), 200
        
    suggestions = SmartSearchEngine.get_suggestions(prefix)
    return jsonify({'success': True, 'suggestions': suggestions}), 200

@search_api.route('/api/v2/vendors/<int:vendor_id>', methods=['GET'])
@login_required
def get_vendor_by_id(vendor_id):
    """API endpoint returning a single vendor's complete master telemetry details."""
    from src.infrastructure.database.models import Vendor
    v = Vendor.query.get(vendor_id)
    if not v:
        return jsonify({'success': False, 'message': 'Vendor profile not found'}), 404
    return jsonify({'success': True, 'vendor': v.to_dict()}), 200

@search_api.route('/api/v2/vendors/search', methods=['GET'])
@login_required
def vendors_list_search():
    """Exposes search route aligned with the client dashboard fetches."""
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'desc')
    category = request.args.get('category')
    trust_level = request.args.get('trust_level')
    
    result = SmartSearchEngine.execute_search(
        query=query,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
        category=category,
        trust_level=trust_level
    )
    return jsonify(result), 200

@search_api.route('/api/v2/vendors', methods=['GET', 'POST'])
@login_required
def vendors_crud_gateway():
    """Handles GET list/search and POST creation for vendor records."""
    from src.infrastructure.database.models import db, Vendor
    
    if request.method == 'POST':
        data = request.get_json() or {}
        email = data.get('email', 'vendor@enterprise.local')
        gst_number = data.get('gst_number', '27AAAAA0000A1Z5')
        
        # Check for existing vendor with matching email or GSTIN to maintain unique identifiers
        existing = Vendor.query.filter((Vendor.email == email) | (Vendor.gst_number == gst_number)).first()
        if existing:
            existing.name = data.get('name', existing.name)
            existing.category = data.get('category', existing.category)
            existing.phone = data.get('phone', existing.phone)
            existing.address = data.get('address', existing.address)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Vendor profile updated successfully', 'vendor': existing.to_dict()}), 200

        new_v = Vendor(
            name=data.get('name', 'New Enterprise Vendor'),
            category=data.get('category', 'General Procurement'),
            email=email,
            phone=data.get('phone', '+91 9000000000'),
            address=data.get('address', 'Mumbai, Maharashtra'),
            gst_number=gst_number,
            pan_number=data.get('pan_number', 'AAAAA0000A'),
            bank_account=data.get('bank_account', '1234567890'),
            trust_score=75.0,
            status='Active'
        )
        db.session.add(new_v)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor created successfully', 'vendor': new_v.to_dict()}), 201
    
    # GET method handling search & category parameters
    search_q = request.args.get('search', request.args.get('q', request.args.get('query', '')))
    cat_q = request.args.get('category')
    
    result = SmartSearchEngine.execute_search(
        query=search_q,
        category=cat_q,
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 50))
    )
    return jsonify(result), 200
