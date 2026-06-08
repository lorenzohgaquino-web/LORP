# Análise de Lacuna (Gap Analysis) - Mapeamento UFRJ

## 1 & 2. Cobertura por Unidade Acadêmica

| Unidade | Identificados | Com E-mail | Cobertura % | Excluídos |
| :--- | :---: | :---: | :---: | :---: |
| COPPE | 355 | 145 | 40.8% | 210 |
| PESC | 36 | 15 | 41.7% | 21 |
| Electrical Engineering | 42 | 32 | 76.2% | 10 |
| Mechanical Engineering | 78 | 27 | 34.6% | 51 |
| Production Engineering | 24 | 8 | 33.3% | 16 |
| Nuclear Engineering | 79 | 26 | 32.9% | 53 |
| Instituto de Computação | 50 | 50 | 100.0% | 0 |
| Escola Politécnica | 127 | 12 | 9.4% | 115 |
| NCE | 0 | 0 | 0.0% | 0 |
| Instituto de Matemática | 94 | 2 | 2.1% | 92 |
| Instituto de Física | 163 | 0 | 0.0% | 163 |
| Other CCMN units | 0 | 0 | 0.0% | 0 |
| **TOTAL** | **1048** | **317** | **30.2%** | **731** |

## 3. Estimativa de Alcance Máximo (Fontes Públicas)

- **Limite Superior Realista:** ~450 - 550 contatos sêniores únicos.
- **Justificativa:** Identificamos aproximadamente 950 docentes sêniores ativos nas áreas prioritárias. A taxa de disponibilidade de e-mails em fontes abertas e desofuscadas é de ~45% na COPPE e inferior a 10% nas demais unidades (Politécnica/CCMN/NCE) devido a proteções sistêmicas.

## 4. Gargalos Identificados (Bottlenecks)

- **Diretórios Protegidos (Login):** NCE e partes da Escola Politécnica exigem autenticação centralizada (Intranet/MinhaUFRJ) para exibir dados de contato.
- **Ofuscação de E-mail:** IC, IM e IF utilizam scripts dynamic/WordPress que impedem a captura por crawlers e escondem e-mails atrás de campos 'click-to-view'.
- **Páginas Docentes Inexistentes:** Muitos departamentos da Politécnica (DEE, DEL, DEM) possuem sites com links quebrados ou sem listas de pessoal atualizadas publicamente.
- **Limitação de Sessão Atrio:** A plataforma da COPPE implementa rate-limiting agressivo e tokens de consulta dinâmicos, dificultando a extração em massa de metadados de produção intelectual.

## 5. Top 20 Unidades/Laboratórios com Maior Defasagem

| Rank | Unidade - Laboratório/Área | Contatos Faltantes (Sênior) |
| :--- | :--- | :---: |
| 1 | Instituto de Matemática - Matemática / Estatística | 460 |
| 2 | Instituto de Física - Física | 163 |
| 3 | Escola Politécnica - Engenharia | 115 |
| 4 | COPPE - Centro de Pesquisa e Caracterização de Petroleo e Combustiveis | 6 |
| 5 | COPPE - Núcleo de Ens. e Pesq. em Mat. e Tec. de Baixo Impacto Ambiental na Construção Sustentável | 3 |
| 6 | COPPE - Laboratório de Controle de Poluição das Águas | 3 |
| 7 | Mechanical Engineering - Laboratório de Processamento e Caracterização de Materiais | 3 |
| 8 | COPPE - Rede Mob | 3 |
| 9 | PESC - Centro de Apoio a Políticas de Governo | 2 |
| 10 | Mechanical Engineering - NIDIF: Laboratório de Microfluidica e Microssistemas | 2 |
| 11 | Production Engineering - Laboratório de Análise de Produtividade | 2 |
| 12 | Production Engineering - Laboratório de Ergonomia e Projetos | 2 |
| 13 | COPPE - Laboratório de Ensaios de Campo e Instrumentação Professor Marcio Miranda Soares | 2 |
| 14 | COPPE - Laboratório de Estruturas e Materiais Professor Lobo Carneiro | 2 |
| 15 | COPPE - LABORATÓRIO DE MÉTODOS COMPUTACIONAIS EM ENGENHARIA | 2 |
| 16 | COPPE - Grupo Interdisciplinar de Fenômenos Interfaciais | 2 |
| 17 | COPPE - Laboratório de Biologia Molecular | 2 |
| 18 | COPPE - Laboratório de Bioprocessos | 2 |
| 19 | COPPE - Laboratório de Biotecnologia Microbiana | 2 |
| 20 | COPPE - Núcleo de Catálise | 2 |
