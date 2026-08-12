from flask import Blueprint, request, jsonify
from src.domain.agents.agent_system import AgentOrchestrator
from src.infrastructure.async_jobs.background_job_service import BackgroundJobService
from src.infrastructure.security.decorators import login_required, get_current_user
import logging

agent_api = Blueprint('agent_api', __name__)

@agent_api.route('/api/v2/agents/diagnostic', methods=['GET'])
@login_required
def execute_agent_diagnostic():
    """Triggers the Multi-Agent orchestrator pipeline for a diagnostic task. Supports async background processing."""
    try:
        vendor_id = request.args.get('vendor_id') or request.args.get('id', '101')
        user = get_current_user() or {}
        role = request.headers.get('X-Role') or user.get('role', 'Admin')
        is_async = request.args.get('async') == 'true'
        
        orchestrator = AgentOrchestrator()
        
        if is_async:
            job_id = BackgroundJobService.submit_job(
                job_type='AI Multi-Agent Diagnostic',
                target_fn=orchestrator.run_vendor_diagnostic,
                args=(int(vendor_id), role)
            )
            return jsonify({
                'success': True,
                'message': 'AI diagnostic task queued for background execution.',
                'job_id': job_id,
                'status_url': f"/api/v2/jobs/{job_id}"
            }), 202
            
        from src.infrastructure.database.models import Vendor
        v_obj = Vendor.query.get(int(vendor_id))
        target_id = int(vendor_id) if v_obj else 101
        
        result = orchestrator.run_vendor_diagnostic(target_id, role)
        if not result.get('success'):
            return jsonify(result), 400
            
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error executing agent diagnostics API: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
