# Contrato de Loop - Clareza do Hero

## Resumo para aprovação

**Resultado:** melhorar o hero sem alterar a oferta aprovada
**Entregável:** hero final com evidência de verificação
**PASS:** os critérios congelados passam sem hard failure
**Autonomia:** read_only
**Orçamento:** 4 cycles; 1 retries; 2 no-progress cycles.

## Escopo e evidências

hero atual; oferta aprovada

## Plano de execução

### 1. Congelar o ponto de partida
**O que acontece:** registrar o estado atual e as evidências disponíveis
**Por quê:** estabelecer uma referência confiável antes de qualquer mudança
**Produz:** baseline verificável
**Depois:** usar apenas gaps demonstrados na próxima etapa

### 2. Testar a hipótese principal
**O que acontece:** comparar o baseline com os critérios de decisão congelados
**Por quê:** identificar o principal gap que impede o PASS
**Produz:** gap priorizado e evidência associada
**Depois:** alterar somente o componente responsável pelo gap

### 3. Corrigir o gap verificado
**O que acontece:** aplicar a menor mudança capaz de resolver o gap priorizado
**Por quê:** evitar mudanças de escopo ou otimizações sem evidência
**Produz:** candidato revisado e diff
**Depois:** verificar se a mudança produziu o efeito esperado

## Verificação e convergência

**PASS:** PASS global confirmado
Verifier: revisor independente contra a rubrica congelada
Progress: mudança verificada ou movimento do verifier
No-progress: encerrar após 2 ciclos sem progresso material

## Limites e saídas

**Pode:** scope: hero apenas; side_effect: read_only
**Não pode:** mudança de objetivo, escopo ou boundary
**SUCCESS:** PASS global confirmado
**FAILURE:** bloqueio irrecuperável dentro do escopo
**BUDGET:** orçamento esgotado
**REPLAN:** mudança de objetivo, escopo ou boundary

## Aprovação

A aprovação autoriza somente este contrato. Qualquer replanejamento material exige uma nova aprovação.
