from sqlalchemy import Column, Integer, String, DateTime, Float
from .database import Base

class RegistroFoco(Base):
    __tablename__ = "registros_foco"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campos obrigatórios do desafio
    nivel_foco = Column(Float, nullable=False)  
    tempo_minutos = Column(Integer, nullable=False)
    comentario = Column(String, nullable=False)
    
    # Campos extras 
    categoria = Column(String, default="Geral", index=True) #
    data_registro = Column(DateTime.timezone.utc) 

    def __repr__(self):
        return f"<RegistroFoco(id={self.id}, nivel={self.nivel_foco}, tempo={self.tempo_minutos}min)>"