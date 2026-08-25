# MinMax PT-BR Output regression suite

Use this suite when modifying the skill. The expected result is defined by
properties rather than exact wording so the test does not freeze one acceptable
style into the skill.

## Contents

- R1-R4: over-editing, verb inflation, pronouns, formal register
- R5-R8: lexical continuity, rhythm, repetition, channel calibration
- R9-R12: specificity, asymmetry, gerunds, interpretive relations
- R13-R16: jargon, social voice, epistemic caution, assistant residue
- R17-R20: unresolved ambiguity, protected text, legitimate passive voice, exact contrast
- R21-R26: progressive-loading routing, latent failure detection, maintenance-only evals

For every case, verify factual and semantic preservation first. A stylistic
improvement fails if it changes agency, modality, attribution, chronology,
certainty, scope, or protected terminology.

## R1 - competent prose must not be over-edited

Input:
`A equipe revisou o plano na terça. Duas decisões ficaram em aberto porque ainda faltam dados de churn.`

Expected properties:
- preserve `terça`, two open decisions, the missing churn data, and the causal relation;
- do not add formality, a conclusion, or new context;
- leaving the input unchanged is acceptable.

## R2 - bureaucratic verb inflation

Input:
`O relatório encontra-se disponível e configura-se como a principal referência para a revisão.`

Expected properties:
- simplify marked verb phrases when semantically equivalent;
- preserve that the report is available and is the principal reference;
- do not weaken `principal`.

## R3 - contemporary PT-BR pronoun placement

Input:
`O sistema permite-nos acompanhar o churn por coorte.`

Expected properties:
- prefer contemporary educated Brazilian placement if the register is neutral;
- preserve the exact metric and relation;
- do not translate `churn`.

## R4 - legitimate formal register

Input:
`A decisão constitui precedente relevante para a interpretação do dispositivo.`

Context: legal commentary.

Expected properties:
- do not replace `constitui` merely because `é` is shorter if the legal relation remains natural;
- preserve formal register;
- do not invent the decision, court, article, or precedent details.

## R5 - forced synonym cycling

Input:
`O CRM registra as oportunidades. A plataforma também guarda o histórico. A solução envia alertas.`

Context: all three nouns refer to the same CRM.

Expected properties:
- stabilize the referent instead of cycling generic nouns;
- preserve all three functions;
- do not add integrations or benefits.

## R6 - mechanical paragraph openings

Input:
`Além disso, a equipe reduziu o backlog. Além disso, o tempo de resposta caiu. Além disso, o NPS subiu.`

Expected properties:
- remove mechanical connective repetition;
- preserve all three claims without inventing causality among them;
- do not force a three-part slogan.

## R7 - purposeful repetition

Input:
`Sem dado, não há diagnóstico. Sem diagnóstico, não há prioridade. Sem prioridade, a fila decide.`

Context: deliberate rhetorical passage.

Expected properties:
- preserve the anaphora unless the user explicitly asks for a neutral rewrite;
- do not treat repetition itself as a defect;
- preserve the final metaphorical proposition.

## R8 - channel calibration

Input:
`Venho por meio deste informar que já subi o hotfix em prod e solicito a gentileza de validar.`

Context: Slack message between product and engineering peers.

Expected properties:
- remove displaced officialese;
- keep `hotfix` and `prod` if natural to the team context;
- preserve the request to validate and the completed status of the deploy;
- do not invent a deadline or recipient.

## R9 - technical specificity survives polishing

Input:
`Depois do deploy, o p95 caiu de 820 ms para 410 ms, mas o erro 429 continuou no mesmo nível.`

Expected properties:
- preserve `p95`, both latency values, the 429 error, chronology, and contrast;
- do not generalize to `performance melhorou`;
- do not infer causality beyond `depois do deploy`.

## R10 - asymmetry is allowed

Input:
`O primeiro risco é financeiro e já está quantificado. O segundo ainda não está claro porque depende de uma decisão regulatória que não saiu. Há também um problema menor de treinamento.`

Expected properties:
- preserve different weights and sentence lengths;
- do not normalize the three risks into symmetric bullets unless the artifact calls for a list;
- preserve uncertainty and causal dependence.

## R11 - gerund with a real function

Input:
`Ela entrou na sala falando ao telefone.`

Expected properties:
- keep the gerund because it expresses a clear simultaneous circumstance;
- do not rewrite merely because a gerund exists.

## R12 - sentence-final commentary gerund

Input:
`A taxa caiu 12%, demonstrando a importância da nova política.`

Expected properties:
- preserve both the 12% decline and the asserted interpretive relation;
- make the relation explicit if the gerund sounds like automatic commentary;
- do not downgrade the asserted interpretation to speculation or upgrade it to proof.

## R13 - English calque versus legitimate jargon

Input:
`Precisamos endereçar esse problema no próximo sprint e depois fazer o deploy.`

Expected properties:
- replace the calqued verb if a natural Portuguese verb preserves meaning;
- keep `sprint` and `deploy` when they are established domain terms;
- preserve sequence and obligation.

## R14 - social voice is not neutralized

Input:
`Eu escrevi isso três vezes e ainda estava ruim. Apaguei. Comecei de novo. Melhorou.`

Context: first-person social post.

Expected properties:
- preserve first person, fragments, and abrupt cadence if they are deliberate;
- do not convert into a composed institutional paragraph;
- preserve the exact sequence of actions.

## R15 - competent formal prose can remain formal

Input:
`Embora os resultados sejam promissores, a amostra ainda é insuficiente para sustentar uma conclusão.`

Expected properties:
- preserve concessive structure and epistemic caution;
- do not remove `embora` merely because concessive openings can be overused;
- leaving the sentence substantially unchanged is acceptable.

## R16 - no assistant residue in a finished artifact

Input:
`Claro! Aqui está a análise solicitada. A receita cresceu 8% no trimestre.`

Context: paragraph intended for an executive report.

Expected properties:
- remove conversational assistant residue;
- preserve the 8% quarterly growth claim;
- do not add interpretation.

## R17 - unresolved ambiguity is not guessed away

Input:
`Marina apresentou Laura à sua gerente.`

Context: no information establishes whose manager is meant.

Expected properties:
- do not decide whether the manager belongs to Marina or Laura;
- preserve the ambiguity or surface it outside the artifact when the output contract allows;
- do not invent a reporting relationship.

## R18 - authoritative text remains protected

Input:
`Art. 1o Esta clausula entra em vigor em 1o de janeiro de 2027.`

Context: exact contractual wording quoted inside a document being polished.

Expected properties:
- leave the quoted clause unchanged character for character;
- do not modernize, normalize, or improve its wording;
- editing may resume outside the protected span.

## R19 - legitimate passive voice survives

Input:
`O servidor foi invadido durante a madrugada.`

Context: the agent is unknown.

Expected properties:
- preserve the passive construction or an equally agent-neutral formulation;
- do not invent an attacker or responsible party;
- do not treat passive voice itself as a defect.

## R20 - exact contrast is not flattened

Input:
`O problema nao e demanda; e retencao.`

Context: concise strategic diagnosis; the contrast is intentional.

Expected properties:
- preserve the contrast between demand and retention;
- do not expand it into generic explanatory prose merely to avoid antithesis;
- do not add causes, metrics, or recommendations.

## R21 - routine prose stays core-only

Input:
`A equipe ja enviou a proposta e aguarda o retorno do cliente.`

Context: routine business rewrite.

Expected properties:
- preserve completed send and pending client response;
- do not require grammar, punctuation, naturalness, or editorial references merely because the input is sentence-level prose;
- the core instructions must be sufficient.

## R22 - latent ambiguity still triggers protection

Input:
`Marina falou com Laura depois que sua gerente aprovou o plano.`

Context: generic request to improve the sentence; the user does not mention ambiguity.

Expected properties:
- detect the ambiguous possessive during the reference gate even without an explicit ambiguity request;
- either load the grammar reference or rely on the core ambiguity hard gate;
- do not decide whose manager approved the plan.

## R23 - voice-sensitive text loads naturalness selectively

Input:
`Eu tentei. Nao funcionou. Tentei de novo. Dessa vez foi.`

Context: first-person social post.

Expected properties:
- preserve deliberate fragments and first-person cadence;
- load the naturalness reference when deeper voice calibration is useful;
- do not load punctuation merely because the passage contains periods.

## R24 - punctuation-specific work loads punctuation

Input:
`Ele perguntou: "Voce vai"?`

Context: punctuation review.

Expected properties:
- load the punctuation reference;
- correct quotation/question-mark placement without changing the words or intent;
- do not load unrelated references unless another failure mode is present.

## R25 - structural product copy loads editorial guidance

Input:
`A plataforma transforma dados em decisoes e reune dashboards, alertas e integracoes para que equipes planejem, executem e crescam melhor.`

Context: B2B product-copy rewrite.

Expected properties:
- recognize the structural-calque/product-template risk and load the editorial standard;
- reconstruct relationships rather than perform synonym substitution;
- do not invent mechanisms, metrics, or outcomes.

## R26 - regression suite is maintenance-only

Input:
`Pode deixar este e-mail mais natural?`

Context: ordinary production use.

Expected properties:
- do not load this regression suite as writing guidance;
- use the core and only the production reference needed by the actual text;
- preserve the regression suite for skill maintenance, benchmarking, and stress testing.
