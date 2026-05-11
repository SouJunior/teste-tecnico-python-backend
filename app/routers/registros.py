from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.schemas.registro import (
    DiagnosticoResponse,
    PlanoPomodoroRequest,
    PlanoPomodoroResponse,
    PomodoroCreate,
    RegistroCreate,
    RegistroDiaStatusResponse,
    RegistroResponse,
)
from app.services import diagnostico_service, pomodoro_service, sessao_unica_service
from app.storage import database

router = APIRouter()


def get_dia_referencia(
    dia_referencia: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Dia analisado (YYYY-MM-DD). Padrão: hoje.",
    ),
) -> str:
    return dia_referencia or date.today().isoformat()


def _resposta_plano(dia: str, total_sessoes: int) -> dict:
    """Monta a resposta padronizada de plano Pomodoro com vagas restantes."""
    registradas = database.contar_registros_no_dia("pomodoro", dia)
    return {
        "dia": dia,
        "total_sessoes": total_sessoes,
        "sessoes_registradas": registradas,
        "sessoes_restantes": max(total_sessoes - registradas, 0),
    }


@router.get(
    "/registro-foco/status-dia",
    response_model=RegistroDiaStatusResponse,
    summary="Estado do dia para registro",
    description=(
        "Indica se o plano Pomodoro do dia já existe e quantos blocos faltam; "
        "e se já foi registrada a Sessão única do dia (máximo uma por dia de referência)."
    ),
)
def status_registro_do_dia(
    dia: str = Depends(get_dia_referencia),
) -> RegistroDiaStatusResponse:
    plano = database.obter_plano_pomodoro(dia)
    pomodoro_status = None
    if plano:
        info = _resposta_plano(dia, plano["total_sessoes"])
        pomodoro_status = {
            "total_sessoes": info["total_sessoes"],
            "sessoes_registradas": info["sessoes_registradas"],
            "sessoes_restantes": info["sessoes_restantes"],
        }
    sessao_unica_existe = database.contar_registros_no_dia("sessao_unica", dia) >= 1
    return RegistroDiaStatusResponse(
        dia=dia,
        pomodoro=pomodoro_status,
        sessao_unica_ja_registrada=sessao_unica_existe,
    )


@router.post(
    "/registro-foco",
    response_model=RegistroResponse,
    status_code=201,
    summary="Registrar sessão de foco",
    description=(
        "Registra um bloco de trabalho encerrado. "
        "O campo `metodo` determina o contrato: "
        "`pomodoro` aceita `tempo_pausa_minutos`; "
        "`sessao_unica` aceita `meta_minutos` e `qtd_pausas`."
    ),
)
def criar_registro(
    dados: Annotated[RegistroCreate, Body()],
    dia: str = Depends(get_dia_referencia),
) -> RegistroResponse:
    if isinstance(dados, PomodoroCreate):
        _validar_pode_registrar_pomodoro(dia)
        resultado = pomodoro_service.calcular(dados)
    else:
        _validar_pode_registrar_sessao_unica(dia)
        resultado = sessao_unica_service.calcular(dados)

    registro = {
        **dados.model_dump(mode="json"),
        **resultado,
        "criado_em": dia,
    }
    return database.insert(registro)


def _validar_pode_registrar_pomodoro(dia: str) -> None:
    plano = database.obter_plano_pomodoro(dia)
    if not plano:
        raise HTTPException(
            status_code=400,
            detail="Defina primeiro o plano Pomodoro do dia (quantidade de sessões).",
        )
    registradas = database.contar_registros_no_dia("pomodoro", dia)
    if registradas >= plano["total_sessoes"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Plano Pomodoro completo: {registradas}/{plano['total_sessoes']} blocos registrados. "
                "Para registrar mais, apague um registro ou aumente o plano Pomodoro do dia."
            ),
        )


def _validar_pode_registrar_sessao_unica(dia: str) -> None:
    if database.contar_registros_no_dia("sessao_unica", dia) >= 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Só é permitida uma Sessão única por dia de referência. "
                "Apague o registro existente ou escolha outro dia."
            ),
        )


@router.post(
    "/pomodoro/plano",
    response_model=PlanoPomodoroResponse,
    summary="Definir plano Pomodoro do dia",
    description="Define quantas sessões Pomodoro você pretende realizar hoje.",
)
def definir_plano_hoje(
    payload: PlanoPomodoroRequest,
    dia: str = Depends(get_dia_referencia),
) -> PlanoPomodoroResponse:
    plano = database.definir_plano_pomodoro(dia, payload.total_sessoes)
    return _resposta_plano(plano["dia"], plano["total_sessoes"])


@router.get(
    "/pomodoro/plano",
    response_model=PlanoPomodoroResponse,
    summary="Consultar plano Pomodoro do dia",
)
def obter_plano_hoje(
    dia: str = Depends(get_dia_referencia),
) -> PlanoPomodoroResponse:
    plano = database.obter_plano_pomodoro(dia)
    if not plano:
        raise HTTPException(
            status_code=404,
            detail=f"Plano Pomodoro para {dia} ainda não definido.",
        )
    return _resposta_plano(plano["dia"], plano["total_sessoes"])


@router.get(
    "/diagnostico-produtividade",
    response_model=DiagnosticoResponse,
    summary="Diagnóstico de produtividade",
    description=(
        "Retorna um resumo inteligente das sessões registradas. "
        "Use `mes` (YYYY-MM) para filtrar por mês civil. "
        "Sem filtro, considera todos os registros."
    ),
)
def obter_diagnostico(
    mes: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Filtra por mês no formato YYYY-MM. Exemplo: 2026-05",
    ),
) -> DiagnosticoResponse:
    return diagnostico_service.gerar_diagnostico(mes=mes)


@router.delete(
    "/registros/{registro_id}",
    summary="Apagar um registro",
)
def apagar_registro(registro_id: int) -> dict:
    if not database.delete_registro(registro_id):
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    return {"ok": True}


@router.delete(
    "/registros",
    summary="Apagar todos os registros",
)
def apagar_todos_registros() -> dict:
    database.clear_all()
    return {"ok": True}
