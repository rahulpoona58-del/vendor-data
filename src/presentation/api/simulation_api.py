from flask import Blueprint, request, jsonify
from src.domain.services.simulation_engine import SimulationEngine
from src.infrastructure.security.decorators import login_required
import logging

simulation_api = Blueprint('simulation_api', __name__)

@simulation_api.route('/api/v2/simulation/what-if', methods=['POST'])
@login_required
def run_what_if_simulation():
    """Runs an isolated What-If risk & trust simulation for a vendor profile."""
    try:
        data = request.json or {}
        vendor_id = data.get('vendor_id')
        overrides = data.get('overrides', {})
        
        if not vendor_id:
            return jsonify({'success': False, 'message': 'vendor_id parameter is required'}), 400
            
        result = SimulationEngine.simulate_what_if(int(vendor_id), overrides)
        if not result.get('success'):
            return jsonify(result), 400
            
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"What-if simulation API handler failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@simulation_api.route('/api/v2/simulation/twin/<int:vendor_id>', methods=['GET'])
@login_required
def get_digital_twin(vendor_id):
    """API endpoint retrieving complete digital twin telemetry mirror for a vendor."""
    twin_data = SimulationEngine.simulate_what_if(vendor_id, {})
    return jsonify({'success': True, 'vendor_id': vendor_id, 'twin': twin_data}), 200
