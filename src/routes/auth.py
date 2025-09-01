from flask import Blueprint, request, jsonify
from src.models.auth_key import AuthKey, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login do cliente C#"""
    data = request.get_json()
    
    if not data or 'key' not in data or 'hwid' not in data:
        return jsonify({'success': False, 'message': 'Key e HWID são obrigatórios'}), 400
    
    key_value = data['key']
    hwid = data['hwid']
    
    # Buscar a key no banco
    auth_key = AuthKey.query.filter_by(key_value=key_value).first()
    
    if not auth_key:
        return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
    
    if not auth_key.is_valid():
        return jsonify({'success': False, 'message': 'Key inválida, pausada ou expirada'}), 401
    
    # Se é o primeiro login
    if not auth_key.is_used:
        auth_key.activate_key(hwid)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Login realizado com sucesso - Primeiro acesso',
            'expires_at': auth_key.expires_at.isoformat()
        })
    
    # Se já foi usada, verificar HWID
    if auth_key.hwid != hwid:
        return jsonify({'success': False, 'message': 'HWID não autorizado para esta key'}), 401
    
    return jsonify({
        'success': True, 
        'message': 'Login realizado com sucesso',
        'expires_at': auth_key.expires_at.isoformat()
    })

@auth_bp.route('/keys', methods=['POST'])
def create_keys():
    """Criar novas keys"""
    data = request.get_json()
    
    if not data or 'quantity' not in data or 'expiration_days' not in data:
        return jsonify({'error': 'Quantidade e dias de expiração são obrigatórios'}), 400
    
    try:
        quantity = int(data['quantity'])
        expiration_days = int(data['expiration_days'])
        
        if quantity <= 0 or expiration_days <= 0:
            return jsonify({'error': 'Quantidade e dias devem ser maiores que zero'}), 400
        
        keys = AuthKey.create_keys(quantity, expiration_days)
        
        for key in keys:
            db.session.add(key)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{quantity} keys criadas com sucesso',
            'keys': [key.to_dict() for key in keys]
        })
        
    except ValueError:
        return jsonify({'error': 'Valores inválidos'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/keys', methods=['GET'])
def get_keys():
    """Listar todas as keys"""
    keys = AuthKey.query.all()
    return jsonify({
        'keys': [key.to_dict() for key in keys],
        'total': len(keys)
    })

@auth_bp.route('/keys/<key_value>', methods=['GET'])
def get_key(key_value):
    """Buscar key específica"""
    auth_key = AuthKey.query.filter_by(key_value=key_value).first()
    
    if not auth_key:
        return jsonify({'error': 'Key não encontrada'}), 404
    
    return jsonify(auth_key.to_dict())

@auth_bp.route('/keys/<key_value>', methods=['DELETE'])
def delete_key(key_value):
    """Apagar key específica"""
    auth_key = AuthKey.query.filter_by(key_value=key_value).first()
    
    if not auth_key:
        return jsonify({'error': 'Key não encontrada'}), 404
    
    db.session.delete(auth_key)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Key apagada com sucesso'})

@auth_bp.route('/keys/delete-all', methods=['DELETE'])
def delete_all_keys():
    """Apagar todas as keys"""
    deleted_count = AuthKey.query.delete()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{deleted_count} keys apagadas com sucesso'
    })

@auth_bp.route('/keys/pause-all', methods=['POST'])
def pause_all_keys():
    """Pausar todas as keys"""
    keys = AuthKey.query.all()
    
    for key in keys:
        key.is_paused = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{len(keys)} keys pausadas com sucesso'
    })

@auth_bp.route('/keys/resume-all', methods=['POST'])
def resume_all_keys():
    """Retomar todas as keys"""
    keys = AuthKey.query.all()
    
    for key in keys:
        key.is_paused = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{len(keys)} keys retomadas com sucesso'
    })

@auth_bp.route('/keys/<key_value>/reset-hwid', methods=['POST'])
def reset_key_hwid(key_value):
    """Resetar HWID de uma key específica"""
    auth_key = AuthKey.query.filter_by(key_value=key_value).first()
    
    if not auth_key:
        return jsonify({'error': 'Key não encontrada'}), 404
    
    auth_key.reset_hwid()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'HWID resetado com sucesso'
    })

@auth_bp.route('/logs', methods=['GET'])
def get_logs():
    """Obter logs de todas as keys"""
    keys = AuthKey.query.order_by(AuthKey.created_at.desc()).all()
    
    logs = []
    for key in keys:
        log_entry = {
            'key_value': key.key_value,
            'created_at': key.created_at.isoformat(),
            'first_login_at': key.first_login_at.isoformat() if key.first_login_at else None,
            'status': key.get_status(),
            'hwid': key.hwid,
            'expiration_days': key.expiration_days,
            'expires_at': key.expires_at.isoformat() if key.expires_at else None
        }
        logs.append(log_entry)
    
    return jsonify({
        'logs': logs,
        'total': len(logs)
    })

@auth_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas das keys"""
    total_keys = AuthKey.query.count()
    used_keys = AuthKey.query.filter_by(is_used=True).count()
    paused_keys = AuthKey.query.filter_by(is_paused=True).count()
    active_keys = AuthKey.query.filter(
        AuthKey.is_active == True,
        AuthKey.is_paused == False
    ).count()
    
    # Keys expiradas
    expired_keys = AuthKey.query.filter(
        AuthKey.expires_at != None,
        AuthKey.expires_at < datetime.utcnow()
    ).count()
    
    return jsonify({
        'total_keys': total_keys,
        'used_keys': used_keys,
        'unused_keys': total_keys - used_keys,
        'paused_keys': paused_keys,
        'active_keys': active_keys,
        'expired_keys': expired_keys
    })

