from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string

db = SQLAlchemy()

class Key(db.Model):
    __tablename__ = 'keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    hwid = db.Column(db.String(255), nullable=True)
    expiration_days = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_login_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_paused = db.Column(db.Boolean, default=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relacionamento com logs
    access_logs = db.relationship('AccessLog', backref='key_ref', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Key {self.key_id}>'
    
    @staticmethod
    def generate_unique_key():
        """Gera uma key única de 8 dígitos"""
        while True:
            key = ''.join(random.choices(string.digits, k=8))
            if not Key.query.filter_by(key_id=key).first():
                return key
    
    def is_expired(self):
        """Verifica se a key está expirada"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def activate_key(self, hwid):
        """Ativa a key no primeiro login"""
        if not self.first_login_at:
            self.first_login_at = datetime.utcnow()
            self.expires_at = self.first_login_at + timedelta(days=self.expiration_days)
            self.hwid = hwid
            self.is_used = True
            db.session.commit()
    
    def can_login(self, hwid):
        """Verifica se pode fazer login com esta key"""
        if not self.is_active or self.is_paused:
            return False, "Key inativa ou pausada"
        
        if self.is_expired():
            return False, "Key expirada"
        
        if self.hwid and self.hwid != hwid:
            return False, "HWID não corresponde"
        
        return True, "OK"
    
    def reset_hwid(self):
        """Reseta o HWID da key"""
        self.hwid = None
        self.is_used = False
        self.first_login_at = None
        self.expires_at = None
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_id': self.key_id,
            'hwid': self.hwid,
            'expiration_days': self.expiration_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'first_login_at': self.first_login_at.isoformat() if self.first_login_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_paused': self.is_paused,
            'is_used': self.is_used,
            'is_expired': self.is_expired(),
            'status': self.get_status()
        }
    
    def get_status(self):
        """Retorna o status atual da key"""
        if not self.is_active:
            return "Inativa"
        if self.is_paused:
            return "Pausada"
        if self.is_expired():
            return "Expirada"
        if self.is_used:
            return "Em uso"
        return "Disponível"


class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.String(8), db.ForeignKey('keys.key_id'), nullable=False)
    hwid = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    login_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<AccessLog {self.key_id} - {self.login_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_id': self.key_id,
            'hwid': self.hwid,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_at': self.login_at.isoformat() if self.login_at else None,
            'success': self.success,
            'error_message': self.error_message
        }

