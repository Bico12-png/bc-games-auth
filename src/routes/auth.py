from flask import Blueprint, request, jsonify
from src.models.key import db, Key, AccessLog
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login do cliente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        key_id = data.get('key_id', '').strip()
        hwid = data.get('hwid', '').strip()
        
        if not key_id or not hwid:
            return jsonify({'success': False, 'error': 'Key ID e HWID são obrigatórios'}), 400
        
        if len(key_id) != 8 or not key_id.isdigit():
            return jsonify({'success': False, 'error': 'Key deve ter exatamente 8 dígitos'}), 400
        
        # Buscar a key no banco
        key = Key.query.filter_by(key_id=key_id).first()
        
        if not key:
            # Log de tentativa de login com key inexistente
            log = AccessLog(
                key_id=key_id,
                hwid=hwid,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                error_message='Key não encontrada'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'success': False, 'error': 'Key não encontrada'}), 404
        
        # Verificar se pode fazer login
        can_login, message = key.can_login(hwid)
        
        if not can_login:
            # Log de tentativa de login falhada
            log = AccessLog(
                key_id=key_id,
                hwid=hwid,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                error_message=message
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'success': False, 'error': message}), 403
        
        # Ativar key no primeiro login
        if not key.first_login_at:
            key.activate_key(hwid)
        
        # Log de login bem-sucedido
        log = AccessLog(
            key_id=key_id,
            hwid=hwid,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=True
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'key_info': {
                'key_id': key.key_id,
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'expiration_days': key.expiration_days,
                'first_login': key.first_login_at.isoformat() if key.first_login_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@auth_bp.route('/validate', methods=['POST'])
def validate_key():
    """Endpoint para validar uma key sem fazer login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        key_id = data.get('key_id', '').strip()
        
        if not key_id:
            return jsonify({'success': False, 'error': 'Key ID é obrigatório'}), 400
        
        if len(key_id) != 8 or not key_id.isdigit():
            return jsonify({'success': False, 'error': 'Key deve ter exatamente 8 dígitos'}), 400
        
        # Buscar a key no banco
        key = Key.query.filter_by(key_id=key_id).first()
        
        if not key:
            return jsonify({'success': False, 'error': 'Key não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'key_info': key.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

