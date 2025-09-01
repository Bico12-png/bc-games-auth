from flask import Blueprint, request, jsonify
from src.models.key import db, Key, KeyLog
from datetime import datetime
import random

auth_bp = Blueprint('auth', __name__)

def log_action(key_id, action, details=None, ip_address=None):
    """Registra uma ação no log"""
    log = KeyLog(
        key_id=key_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login do cliente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
            
        key_value = data.get('key')
        hwid = data.get('hwid')
        
        if not key_value or not hwid:
            return jsonify({'success': False, 'message': 'Key e HWID são obrigatórios'}), 400
            
        if len(key_value) != 8 or not key_value.isdigit():
            return jsonify({'success': False, 'message': 'Key deve conter exatamente 8 dígitos'}), 400
            
        # Buscar a chave
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        # Tentar fazer login
        success, message = key.login(hwid)
        
        if success:
            db.session.commit()
            log_action(key.id, 'LOGIN_SUCCESS', f'HWID: {hwid}', request.remote_addr)
            
            return jsonify({
                'success': True,
                'message': message,
                'key_info': {
                    'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                    'days_remaining': (key.expires_at - datetime.utcnow()).days if key.expires_at else key.expiration_days
                }
            })
        else:
            log_action(key.id, 'LOGIN_FAILED', f'HWID: {hwid}, Erro: {message}', request.remote_addr)
            return jsonify({'success': False, 'message': message}), 403
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys', methods=['POST'])
def create_keys():
    """Criar novas chaves"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
            
        quantity = data.get('quantity', 1)
        expiration_days = data.get('expiration_days', 30)
        
        if quantity < 1 or quantity > 1000:
            return jsonify({'success': False, 'message': 'Quantidade deve ser entre 1 e 1000'}), 400
            
        if expiration_days < 1 or expiration_days > 365:
            return jsonify({'success': False, 'message': 'Dias de expiração deve ser entre 1 e 365'}), 400
            
        created_keys = []
        for _ in range(quantity):
            key = Key(expiration_days=expiration_days)
            db.session.add(key)
            db.session.flush()  # Para obter o ID
            created_keys.append(key.key_value)
            log_action(key.id, 'KEY_CREATED', f'Expira em {expiration_days} dias', request.remote_addr)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{quantity} chave(s) criada(s) com sucesso',
            'keys': created_keys
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys', methods=['GET'])
def list_keys():
    """Listar todas as chaves"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        
        query = Key.query
        
        if search:
            query = query.filter(Key.key_value.contains(search))
            
        keys = query.paginate(
            page=page, 
            per_page=min(per_page, 100), 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'keys': [key.to_dict() for key in keys.items],
            'total': keys.total,
            'pages': keys.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/<key_value>', methods=['GET'])
def get_key(key_value):
    """Buscar chave específica"""
    try:
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        return jsonify({
            'success': True,
            'key': key.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/<key_value>', methods=['DELETE'])
def delete_key(key_value):
    """Apagar chave específica"""
    try:
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        log_action(key.id, 'KEY_DELETED', f'Key {key_value} deletada', request.remote_addr)
        db.session.delete(key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Key {key_value} deletada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys', methods=['DELETE'])
def delete_all_keys():
    """Apagar todas as chaves"""
    try:
        count = Key.query.count()
        Key.query.delete()
        KeyLog.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} chave(s) deletada(s) com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/<key_value>/reset-hwid', methods=['POST'])
def reset_hwid(key_value):
    """Resetar HWID de uma chave específica"""
    try:
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        old_hwid = key.hwid
        key.reset_hwid()
        db.session.commit()
        
        log_action(key.id, 'HWID_RESET', f'HWID anterior: {old_hwid}', request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': f'HWID da key {key_value} resetado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/pause-all', methods=['POST'])
def pause_all_keys():
    """Pausar todas as chaves"""
    try:
        keys = Key.query.all()
        count = 0
        
        for key in keys:
            if not key.is_paused:
                key.pause()
                count += 1
                log_action(key.id, 'KEY_PAUSED', 'Pausada em lote', request.remote_addr)
                
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} chave(s) pausada(s) com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/unpause-all', methods=['POST'])
def unpause_all_keys():
    """Despausar todas as chaves"""
    try:
        keys = Key.query.all()
        count = 0
        
        for key in keys:
            if key.is_paused:
                key.unpause()
                count += 1
                log_action(key.id, 'KEY_UNPAUSED', 'Despausada em lote', request.remote_addr)
                
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} chave(s) despausada(s) com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/<key_value>/pause', methods=['POST'])
def pause_key(key_value):
    """Pausar chave específica"""
    try:
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        key.pause()
        db.session.commit()
        
        log_action(key.id, 'KEY_PAUSED', f'Key {key_value} pausada', request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': f'Key {key_value} pausada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/keys/<key_value>/unpause', methods=['POST'])
def unpause_key(key_value):
    """Despausar chave específica"""
    try:
        key = Key.query.filter_by(key_value=key_value).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key não encontrada'}), 404
            
        key.unpause()
        db.session.commit()
        
        log_action(key.id, 'KEY_UNPAUSED', f'Key {key_value} despausada', request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': f'Key {key_value} despausada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/logs', methods=['GET'])
def get_logs():
    """Obter logs das chaves"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        logs = KeyLog.query.order_by(KeyLog.timestamp.desc()).paginate(
            page=page,
            per_page=min(per_page, 100),
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas das chaves"""
    try:
        total_keys = Key.query.count()
        used_keys = Key.query.filter_by(is_used=True).count()
        paused_keys = Key.query.filter_by(is_paused=True).count()
        expired_keys = Key.query.filter(Key.expires_at < datetime.utcnow()).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_keys': total_keys,
                'used_keys': used_keys,
                'unused_keys': total_keys - used_keys,
                'paused_keys': paused_keys,
                'expired_keys': expired_keys,
                'active_keys': used_keys - expired_keys - paused_keys
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

