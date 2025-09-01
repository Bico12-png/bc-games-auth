from src.models.user import db
from datetime import datetime, timedelta
import random
import string

class Key(db.Model):
    __tablename__ = 'keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(8), unique=True, nullable=False, index=True)
    hwid = db.Column(db.String(255), nullable=True)
    expiration_days = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_login_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    is_paused = db.Column(db.Boolean, default=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)
    
    def __init__(self, expiration_days):
        self.key_value = self.generate_unique_key()
        self.expiration_days = expiration_days
        
    @staticmethod
    def generate_unique_key():
        """Gera uma chave única de 8 dígitos"""
        while True:
            key = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            if not Key.query.filter_by(key_value=key).first():
                return key
    
    def activate_key(self, hwid):
        """Ativa a chave no primeiro login"""
        if not self.is_used:
            self.hwid = hwid
            self.is_used = True
            self.first_login_at = datetime.utcnow()
            self.expires_at = datetime.utcnow() + timedelta(days=self.expiration_days)
            self.last_login_at = datetime.utcnow()
            self.login_count = 1
            return True
        return False
    
    def is_valid(self, hwid=None):
        """Verifica se a chave é válida"""
        if self.is_paused:
            return False, "Chave pausada pelo administrador"
            
        if not self.is_used:
            return True, "Chave válida para primeiro uso"
            
        if hwid and self.hwid != hwid:
            return False, "HWID não corresponde"
            
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "Chave expirada"
            
        return True, "Chave válida"
    
    def login(self, hwid):
        """Registra um login"""
        is_valid, message = self.is_valid(hwid)
        if not is_valid:
            return False, message
            
        if not self.is_used:
            self.activate_key(hwid)
        else:
            self.last_login_at = datetime.utcnow()
            self.login_count += 1
            
        return True, "Login realizado com sucesso"
    
    def reset_hwid(self):
        """Reseta o HWID da chave"""
        self.hwid = None
        return True
    
    def pause(self):
        """Pausa a chave"""
        self.is_paused = True
        
    def unpause(self):
        """Despausa a chave"""
        self.is_paused = False
    
    def to_dict(self):
        """Converte para dicionário"""
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
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'login_count': self.login_count,
            'status': 'Pausada' if self.is_paused else ('Expirada' if self.expires_at and datetime.utcnow() > self.expires_at else ('Em uso' if self.is_used else 'Não utilizada'))
        }

class KeyLog(db.Model):
    __tablename__ = 'key_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('keys.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    key = db.relationship('Key', backref=db.backref('logs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_value': self.key.key_value if self.key else None,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }

