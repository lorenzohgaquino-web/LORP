# DOCUMENTAÇÃO METODOLÓGICA — UFU (LARGA ESCALA)

## 1. DESCOBERTA E EXTRAÇÃO
*   **Mapeamento de Alvos:** Identificação de todas as unidades tecnológicas da UFU em Uberlândia e campi avançados.
*   **Crawler Multi-Camada:** Desenvolvimento de scripts capazes de ler listas de docentes e, recursivamente, acessar perfis individuais quando o contato principal estava oculto na listagem.
*   **Análise Semântica:** Uso de expressões regulares para extrair nomes de laboratórios e programas de pós-graduação diretamente das biografias e portarias publicadas nos sites.

## 2. TRATAMENTO E NORMALIZAÇÃO
*   **Consolidação de Identidade:** Tratamento de nomes com e sem acentos para evitar duplicidade de docentes que atuam em diferentes unidades.
*   **Priorização de Qualidade:** Em caso de registros conflitantes, priorizou-se a fonte com metadados mais recentes e e-mails validados (@ufu.br).
*   **Remoção de 'Noise':** Filtros rigorosos para remover elementos de navegação (como botões de 'Lattes' ou 'Plano de Trabalho') que ocasionalmente são capturados como nomes por crawlers genéricos.

## 3. VALIDAÇÃO DE CAMPOS (14 CAMPOS OBRIGATÓRIOS)
O dataset segue rigorosamente a estrutura solicitada, preenchendo vínculos institucionais, URLs de fonte e status de verificação para cada um dos 803 registros.
