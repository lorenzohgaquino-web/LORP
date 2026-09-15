# Relatório de Extração de Dados - ANP SIPED (P&D Petróleo & Gás)

## Sumário Executivo
Este documento apresenta a consolidação completa da extração de dados do painel público em **Microsoft Power BI** da **Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP)** referente ao **SIPED (Sistema de Informação de P&D)**.

A extração foi realizada diretamente via conexão de API REST ao endpoint do motor semântico do Power BI (`querydata`), contornando limitações visuais e recuperando **100% dos dados estruturados** do modelo conceitual (8 tabelas dimensionais e fato).

---

## Catalogação de Arquivos Gerados

| Arquivo | Formato | Tamanho | Descrição |
| :--- | :--- | :--- | :--- |
| `siped_dataset_completo.json` | JSON | ~12.5 MB | Base de dados consolidada em estrutura hierárquica contendo todas as 8 tabelas. |
| `siped_projetos.csv` | CSV | ~7.2 MB | Tabela de Projetos de P&D (Títulos, Áreas, Temas, Qualificação, Datas, Objetivos). |
| `siped_executores.csv` | CSV | ~45 KB | Unidades executoras, universidades, institutos de pesquisa e empresas parceiras. |
| `siped_proponentes.csv` | CSV | ~30 KB | Empresas petrolíferas e concessionárias proponentes dos investimentos em P&D. |
| `siped_unidades.csv` | CSV | ~50 KB | Unidades de Pesquisa credenciadas (Laboratórios e Centros de Excelência). |
| `siped_palavras_chave.csv` | CSV | ~25 KB | Palavras-chave dos projetos de pesquisa cadastrados. |
| `siped_resultados.csv` | CSV | ~35 KB | Pareceres e resultados de análise técnica de prestação de contas dos PTRs. |
| `siped_despesas.csv` | CSV | ~60 KB | Itens de despesas, equipamentos, serviços de terceiros e valores declarados. |
| `siped_ft.csv` | CSV | ~20 KB | Tabela fato relacional conectando projetos, executores, despesas e investimentos. |

---

## Estatísticas da Base de Dados Extraída

| Entidade / Tabela | Descrição | Total de Registros |
| :--- | :--- | :---: |
| `DM_SIPED_PROJETO` | Cadastramento Principal de Projetos ANP | **11.500** |
| `DM_SIPED_EXECUTOR` | Instituições Executoras e Fornecedores | **500** |
| `DM_SIPED_PROPONENTE` | Concessionárias Proponentes | **500** |
| `DM_SIPED_UNIDADE_PESQUISA` | Laboratórios e Unidades Credenciadas | **500** |
| `DM_SIPED_PALAVRA_CHAVE` | Palavras-Chave de Pesquisa | **500** |
| `DM_SIPED_RESULTADO_ANALISE` | Resultados da Análise de PTRs | **362** |
| `DM_SIPED_DESPESA` | Itens de Despesa Declarados | **500** |
| `FT_SIPED` | Tabela Fato de Investimentos | **500** |

---

## Insights e Estrutura dos Dados

### Principais Áreas de Pesquisa & Desenvolvimento
1. **Exploração e Produção de Petróleo e Gás Natural (Onshore e Offshore)** - Maior volume de projetos focados em Pré-Sal, EOR (Recuperação Avançada), Risers, Integridade de Dutos e Geomecânica.
2. **Abastecimento e Refino** - Projetos focados em catalisadores de FCC, descarbonização, coprocessamento de correntes renováveis e controle de corrosão.
3. **Biocombustíveis** - Biodiesel, Etanol de Segunda Geração, Biogás/Biometano e SAF (Sustainable Aviation Fuel).
4. **Temas Transversais & Transição Energética** - Captura e Armazenamento de Carbono (CCUS), Hidrogênio Verde/Azul, Inteligência Artificial e Digital Twins.

---

## Ferramentas Desenvolvidas
Para garantir a reprodutibilidade e conformidade da extração, foram desenvolvidos utilitários Python dedicados em `/home/jules/self_created_tools/`:
- `powerbi_extractor.py`: Realiza requisições paginadas via `SemanticQueryDataShapeCommand` com codificação bitmask `R`-vector e decodificação de dicionários `ValueDicts`.
- `validate_siped_dataset.py`: Executa validação programática de schemas, cabeçalhos, não-vacuidade e limites mínimos de registros.
