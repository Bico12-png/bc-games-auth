from flask import Blueprint, request, jsonify
from src.models.key import db, Key, AccessLog
from datetime import datetime
from sqlalchemy import desc

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/keys', methods=['POST'])
def create_keys():
    """Criar novas keys"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        quantity = data.get('quantity', 1)
        expiration_days = data.get('expiration_days', 30)
        
        if not isinstance(quantity, int) or quantity < 1 or quantity > 100:
            return jsonify({'success': False, 'error': 'Quantidade deve ser entre 1 e 100'}), 400
        
        if not isinstance(expiration_days, int) or expiration_days < 1 or expiration_days > 365:
            return jsonify({'success': False, 'error': 'Dias de expiração deve ser entre 1 e 365'}), 400
        
        created_keys = []
        
        for _ in range(quantity):
            key_id = Key.generate_unique_key()
            new_key = Key(
                key_id=key_id,
                expiration_days=expiration_days
            )
            db.session.add(new_key)
            created_keys.append(key_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{quantity} key(s) criada(s) com sucesso',
            'keys': created_keys,
            'expiration_days': expiration_days
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys', methods=['GET'])
def list_keys():
    """Listar todas as keys com paginação"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        
        if per_page > 100:
            per_page = 100
        
        query = Key.query
        
        # Filtro de busca por key_id
        if search:
            query = query.filter(Key.key_id.like(f'%{search}%'))
        
        # Filtro por status
        if status_filter:
            if status_filter == 'active':
                query = query.filter(Key.is_active == True, Key.is_paused == False)
            elif status_filter == 'paused':
                query = query.filter(Key.is_paused == True)
            elif status_filter == 'inactive':
                query = query.filter(Key.is_active == False)
            elif status_filter == 'used':
                query = query.filter(Key.is_used == True)
            elif status_filter == 'unused':
                query = query.filter(Key.is_used == False)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(desc(Key.created_at))
        
        # Paginação
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        keys = [key.to_dict() for key in pagination.items]
        
        return jsonify({
            'success': True,
            'keys': keys,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys/<key_id>', methods=['GET'])
def get_key(key_id):
    """Buscar key específica"""
    try:
        if len(key_id) != 8 or not key_id.isdigit():
            return jsonify({'success': False, 'error': 'Key deve ter exatamente 8 dígitos'}), 400
        
        key = Key.query.filter_by(key_id=key_id).first()
        
        if not key:
            return jsonify({'success': False, 'error': 'Key não encontrada'}), 404
        
        # Buscar logs da key
        logs = AccessLog.query.filter_by(key_id=key_id).order_by(desc(AccessLog.login_at)).limit(10).all()
        
        return jsonify({
            'success': True,
            'key': key.to_dict(),
            'recent_logs': [log.to_dict() for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys/<key_id>', methods=['DELETE'])
def delete_key(key_id):
    """Apagar key específica"""
    try:
        if len(key_id) != 8 or not key_id.isdigit():
            return jsonify({'success': False, 'error': 'Key deve ter exatamente 8 dígitos'}), 400
        
        key = Key.query.filter_by(key_id=key_id).first()
        
        if not key:
            return jsonify({'success': False, 'error': 'Key não encontrada'}), 404
        
        db.session.delete(key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Key {key_id} apagada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys/delete-all', methods=['DELETE'])
def delete_all_keys():
    """Apagar todas as keys"""
    try:
        # Contar quantas keys serão apagadas
        count = Key.query.count()
        
        if count == 0:
            return jsonify({
                'success': True,
                'message': 'Nenhuma key encontrada para apagar'
            }), 200
        
        # Apagar todas as keys (logs serão apagados automaticamente devido ao cascade)
        Key.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} key(s) apagada(s) com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys/<key_id>/reset-hwid', methods=['POST'])
def reset_key_hwid(key_id):
    """Resetar HWID de uma key específica"""
    try:
        if len(key_id) != 8 or not key_id.isdigit():
            return jsonify({'success': False, 'error': 'Key deve ter exatamente 8 dígitos'}), 400
        
        key = Key.query.filter_by(key_id=key_id).first()
        
        if not key:
            return jsonify({'success': False, 'error': 'Key não encontrada'}), 404
        
        key.reset_hwid()
        
        return jsonify({
            'success': True,
            'message': f'HWID da key {key_id} resetado com sucesso',
            'key': key.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/keys/pause-all', methods=['POST'])
def pause_all_keys():
    """Pausar todas as keys"""
    try:
        data = request.get_json() or {}
        pause = data.get('pause', True)
        
        # Atualizar todas as keys
        count = Key.query.filter(Key.is_active == True).update({'is_paused': pause})
        db.session.commit()
        
        action = "pausadas" if pause else "despausadas"
        
        return jsonify({
            'success': True,
            'message': f'{count} key(s) {action} com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/logs', methods=['GET'])
def get_logs():
    """Obter logs de acesso"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        key_id = request.args.get('key_id', '').strip()
        success_only = request.args.get('success_only', '').lower() == 'true'
        
        if per_page > 100:
            per_page = 100
        
        query = AccessLog.query
        
        # Filtro por key_id
        if key_id:
            query = query.filter(AccessLog.key_id.like(f'%{key_id}%'))
        
        # Filtro por sucesso
        if success_only:
            query = query.filter(AccessLog.success == True)
        
        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(desc(AccessLog.login_at))
        
        # Paginação
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        logs = [log.to_dict() for log in pagination.items]
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas do sistema"""
    try:
        total_keys = Key.query.count()
        active_keys = Key.query.filter(Key.is_active == True, Key.is_paused == False).count()
        paused_keys = Key.query.filter(Key.is_paused == True).count()
        used_keys = Key.query.filter(Key.is_used == True).count()
        expired_keys = Key.query.filter(Key.expires_at < datetime.utcnow()).count()
        
        total_logins = AccessLog.query.count()
        successful_logins = AccessLog.query.filter(AccessLog.success == True).count()
        failed_logins = AccessLog.query.filter(AccessLog.success == False).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'keys': {
                    'total': total_keys,
                    'active': active_keys,
                    'paused': paused_keys,
                    'used': used_keys,
                    'expired': expired_keys,
                    'available': total_keys - used_keys - expired_keys
                },
                'logins': {
                    'total': total_logins,
                    'successful': successful_logins,
                    'failed': failed_logins,
                    'success_rate': round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

