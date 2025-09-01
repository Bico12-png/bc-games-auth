from src.extensions import db
from datetime import datetime, timedelta
import random
import string

class AuthKey(db.Model):
    __tablename__ = 'auth_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(8), unique=True, nullable=False)
    hwid = db.Column(db.String(255), nullable=True)
    expiration_days = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_login_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    is_paused = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<AuthKey {self.key_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_value': self.key_value,
            'hwid': self.hwid,
            'expiration_days': self.expiration_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'first_login_at': self.first_login_at.isoformat() if self.first_login_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used': self.is_used,
            'is_paused': self.is_paused,
            'is_active': self.is_active,
            'status': self.get_status()
        }
    
    def get_status(self):
        if not self.is_active:
            return 'Inativa'
        if self.is_paused:
            return 'Pausada'
        if not self.is_used:
            return 'Não utilizada'
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return 'Expirada'
        return 'Ativa'
    
    def is_valid(self):
        if not self.is_active or self.is_paused:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def activate_key(self, hwid):
        """Ativa a key no primeiro login"""
        if not self.is_used:
            self.hwid = hwid
            self.first_login_at = datetime.utcnow()
            self.expires_at = datetime.utcnow() + timedelta(days=self.expiration_days)
            self.is_used = True
            return True
        return False
    
    def reset_hwid(self):
        """Reseta o HWID da key"""
        self.hwid = None
        self.first_login_at = None
        self.expires_at = None
        self.is_used = False
    
    @staticmethod
    def generate_unique_key():
        """Gera uma key única de 8 dígitos"""
        while True:
            key = ''.join(random.choices(string.digits, k=8))
            if not AuthKey.query.filter_by(key_value=key).first():
                return key
    
    @staticmethod
    def create_keys(quantity, expiration_days):
        """Cria múltiplas keys"""
        keys = []
        for _ in range(quantity):
            key_value = AuthKey.generate_unique_key()
            auth_key = AuthKey(
                key_value=key_value,
                expiration_days=expiration_days
            )
            keys.append(auth_key)
        return keys

