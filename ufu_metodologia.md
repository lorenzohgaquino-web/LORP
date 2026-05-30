# DOCUMENTAÇÃO METODOLÓGICA — UFU (REVISADA)

## 1. METODOLOGIA DE EXTRAÇÃO
A coleta foi realizada através de um crawler especializado em arquiteturas Drupal (CMS padrão da UFU):
*   **Mapeamento de Perfis:** Identificação de nodes do tipo 'pessoa' e extração individualizada.
*   **Captura de Metadados:** Uso de expressões regulares para identificar vínculos com Laboratórios, Grupos de Pesquisa e Programas de Pós-Graduação (PPGs) dentro do texto biográfico dos docentes.
*   **Verificação Cruzada:** Consulta aos sites de Pós-Graduação para obter e-mails de pesquisadores que não constavam nas páginas de graduação.

## 2. GARANTIA DE QUALIDADE
*   **Limpeza de E-mails:** Scripts de pós-processamento removeram prefixos espúrios (como 'lattes') capturados durante o scrape de links mal estruturados.
*   **Deduplicação:** Consolidação de registros repetidos (docentes que atuam em graduação e pós-graduação simultaneamente).
*   **Normalização:** Nomes e cargos padronizados para consistência do banco de dados.

## 3. ABRANGÊNCIA
O dataset cobre as áreas de Computação, Engenharias (Elétrica, Mecânica, Aeronáutica, Mecatrônica, Biomédica, Química, Civil), Física e Matemática, incluindo os campi de Uberlândia (Santa Mônica/Umuarama/Glória), Patos de Minas, Monte Carmelo e Ituiutaba (Pontal).
