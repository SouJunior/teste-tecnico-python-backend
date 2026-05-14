from typing import List
from .models import RegistroFoco

class PerformanceService:
    @staticmethod
    def gerar_diagnostico(registros: List[RegistroFoco]):
        # Se não houver registros, retornamos None para o main tratar o erro
        if not registros:
            return None

        # Cálculos (A lógica que estava no main)
        total_minutos = sum(r.tempo_minutos for r in registros)
        total_sessoes = len(registros)
        media_foco = sum(r.nivel_foco for r in registros) / total_sessoes
        
        # Lógica de Feedback
        if media_foco >= 4.5:
            feedback = "Incrível! Você está em estado de flow constante. Continue assim!"
        elif media_foco > 3.0:
            feedback = "Você teve uma boa performance. Tente reduzir pequenas distrações."
        elif media_foco >= 2.5:
            feedback = "Produtividade mediana. Talvez pausas mais longas ajudem a recuperar o foco."
        else:
            feedback = "Alerta de distração: Sugerimos desligar notificações e usar a técnica Pomodoro."

        return {
            "media_foco": round(media_foco, 2),
            "tempo_total_focado": total_minutos,
            "total_sessoes": total_sessoes,
            "mensagem_feedback": feedback
        }