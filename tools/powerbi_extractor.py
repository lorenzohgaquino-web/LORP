#!/usr/bin/env python3
"""
Power BI SIPED Data Extractor
Extracts 100% of data from the ANP SIPED Power BI report embedded endpoint.
"""

import os
import sys
import json
import csv
import time
import argparse
import urllib.request
import urllib.error

ENDPOINT_URL = "https://wabi-brazil-south-d-primary-api.analysis.windows.net/public/reports/querydata?synchronous=true"
RESOURCE_KEY = "e91dbe81-348b-48a5-970a-5ee87e09a9b2"
MODEL_ID = 433514
DATASET_ID = "350d7940-9d44-46b8-ab5e-522ed6d296ed"
REPORT_ID = "37b4c53e-c359-4821-9848-67058f274a91"

TABLE_SCHEMAS = {
    "DM_SIPED_PROJETO": {
        "order_prop": "NUM_PROJETO_ANP",
        "is_numeric": False,
        "props": [
            "NUM_PROJETO_ANP", "DSC_TITULO", "NOM_AREA", "NOM_TEMA", "NOM_SUB_TEMA",
            "DSC_QUALIFICACAO", "NOM_EMP_CARGA", "NUM_PRAZO_MES", "DAT_CONTRATACAO",
            "PREV_CONCLUSAO", "DAT_CONCLUSAO", "DSC_FINALIDADE", "DSC_OBJETIVO",
            "COD_REGULAMENTO_TECNICO", "ANO_AUTORIZACAO", "NUM_AUTORIZACAO",
            "IND_CONTRATACAO", "IND_ULT_TIPO", "IND_ATUAL"
        ],
        "csv_filename": "siped_projetos.csv"
    },
    "DM_SIPED_EXECUTOR": {
        "order_prop": "SK_SEQ_EXECUTOR",
        "is_numeric": True,
        "props": [
            "SK_SEQ_EXECUTOR", "NK_SEQ_EXECUTOR", "NK_SEQ_PROJETO", "NOM_PESSOA",
            "NOM_FANTASIA", "NUM_CNPJ", "DSC_TIPO_EXECUTOR", "IND_BASE_TECNOLOGICA",
            "IND_PORTE_EMPRESA", "IND_TIPO_INSTITUICAO", "IND_FINS_LUCRATIVOS",
            "VAL_RECEITA_FINANCEIRA", "SIG_UF"
        ],
        "csv_filename": "siped_executores.csv"
    },
    "DM_SIPED_PROPONENTE": {
        "order_prop": "NK_SEQ_PROPONENTE",
        "is_numeric": True,
        "props": [
            "NK_SEQ_PROPONENTE", "NK_SEQ_PROJETO", "NOM_FANTASIA", "NUM_CNPJ",
            "PCT_RECURSO", "NOM_LOCALIDADE", "NOM_BAIRRO", "SIG_UF", "Valor_PTR_proponente_"
        ],
        "csv_filename": "siped_proponentes.csv"
    },
    "DM_SIPED_UNIDADE_PESQUISA": {
        "order_prop": "SK_SEQ_UNIDADE_PESQUISA",
        "is_numeric": True,
        "props": [
            "SK_SEQ_UNIDADE_PESQUISA", "NK_SEQ_UNIDADE_PESQUISA", "NUM_CREDENCIAMENTO",
            "NUM_PROCESSO", "DSC_SITUACAO_CREDENCIAMENTO", "NOM_UNIDADE_PESQUISA",
            "NOM_APELIDO_UNIDADE_PESQUISA", "SIG_UNIDADE_PESQUISA", "NUM_CNPJ",
            "NOM_UO", "SIG_UO", "NOM_MUNICIPIO", "UF", "NOM_BAIRRO", "NOM_COORDENADOR",
            "IND_CREDENCIADA"
        ],
        "csv_filename": "siped_unidades.csv"
    },
    "DM_SIPED_PALAVRA_CHAVE": {
        "order_prop": "SK_SEQ_PALAVRA_CHAVE",
        "is_numeric": True,
        "props": [
            "SK_SEQ_PALAVRA_CHAVE", "NK_SEQ_PALAVRA_CHAVE", "NK_SEQ_PROJETO",
            "DSC_PALAVRA_CHAVE", "SIG_ORIGEM"
        ],
        "csv_filename": "siped_palavras_chave.csv"
    },
    "DM_SIPED_RESULTADO_ANALISE": {
        "order_prop": "SK_SEQ_PTR_RSLTO_ANLSE_PTR",
        "is_numeric": True,
        "props": [
            "SK_SEQ_PTR_RSLTO_ANLSE_PTR", "SEQ_PTR_RSLTO_ANLSE_PTR", "NK_SEQ_PROJETO",
            "NOM_PESSOA", "NUM_PROTOCOLO_SEI", "DAT_PARECER", "DSC_RESULTADO_ANALISE",
            "VAL_ENQUADRADO", "VAL_NAO_ENQUADRADO", "DSC_OBSERVACAO"
        ],
        "csv_filename": "siped_resultados.csv"
    },
    "DM_SIPED_DESPESA": {
        "order_prop": "SK_SEQ_DESPESA",
        "is_numeric": True,
        "props": [
            "SK_SEQ_DESPESA", "NK_SEQ_DESPESA", "NK_SEQ_PROJETO", "NUM_ITEM_DESPESA",
            "IND_PROCEDENCIA_BEM", "DSC_DESPESA", "DSC_JUSTIFICATIVA", "DSC_TIPO_DESPESA",
            "DSC_ELEMENTO_DESPESA", "VAL_UNITARIO_BEM_SERVICO", "VAL_TOTAL_DECLARADO"
        ],
        "csv_filename": "siped_despesas.csv"
    },
    "FT_SIPED": {
        "order_prop": "SK_SEQ_PROJETO",
        "is_numeric": True,
        "props": [
            "SK_SEQ_PROJETO", "SK_SEQ_UNIDADE_PESQUISA", "SK_SEQ_EXECUTOR", "SK_SEQ_DESPESA",
            "VAL_TRATADO", "Executor", "executor2"
        ],
        "csv_filename": "siped_ft.csv"
    }
}


def decode_ph(ph_list, props, value_dicts):
    rows = []
    current_values = [None] * len(props)

    if not ph_list or "DM0" not in ph_list[0]:
        return rows

    dm0 = ph_list[0]["DM0"]
    for item in dm0:
        c = item.get("C", [])
        r_mask = item.get("R", 0)

        c_idx = 0
        row_vals = []
        for i in range(len(props)):
            bit = (r_mask >> i) & 1
            if bit == 1:
                row_vals.append(current_values[i])
            else:
                if c_idx < len(c):
                    val = c[c_idx]
                    c_idx += 1
                    dict_key = f"D{i}"
                    if dict_key in value_dicts and isinstance(val, int) and val < len(value_dicts[dict_key]):
                        val = value_dicts[dict_key][val]
                    row_vals.append(val)
                else:
                    row_vals.append(None)

        current_values = list(row_vals)
        rows.append(dict(zip(props, row_vals)))
    return rows


def fetch_page(entity, props, order_prop, is_numeric, last_val=None, count=500, max_retries=5):
    where_clause = []
    if last_val is not None:
        literal_val = str(last_val) if is_numeric else f"'{last_val}'"
        where_clause.append({
            "Condition": {
                "Comparison": {
                    "ComparisonKind": 1, # GreaterThan
                    "Left": {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": order_prop}},
                    "Right": {"Literal": {"Value": literal_val}}
                }
            }
        })
    select_objs = [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": p}, "Name": f"{entity}.{p}"} for p in props]

    query_obj = {
        "Query": {
            "Commands": [
                {
                    "SemanticQueryDataShapeCommand": {
                        "Query": {
                            "Version": 2,
                            "From": [{"Name": "d", "Entity": entity, 'Type': 0}],
                            "Select": select_objs,
                            "Where": where_clause,
                            "OrderBy": [{"Direction": 1, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": order_prop}}}]
                        },
                        "Binding": {
                            "Primary": {"Groupings": [{"Projections": list(range(len(props)))}]},
                            "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": count}}},
                            "Version": 1
                        }
                    }
                }
            ]
        },
        "QueryId": "",
        "ApplicationContext": {"DatasetId": DATASET_ID, "Sources": [{"ReportId": REPORT_ID, "VisualId": "extractor"}]}
    }

    body = {"version": "1.0.0", "queries": [query_obj], "cancelQueries": [], "modelId": MODEL_ID}
    headers = {
        "Content-Type": "application/json",
        "X-PowerBI-ResourceKey": RESOURCE_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    body_bytes = json.dumps(body).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(ENDPOINT_URL, data=body_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(attempt * 2)


def fetch_entire_table(entity, config):
    props = config["props"]
    order_prop = config["order_prop"]
    is_numeric = config["is_numeric"]

    all_rows = []
    last_val = None
    page = 0

    print(f"\n--- Extracting {entity} (Order by: {order_prop}) ---")
    while True:
        page += 1
        try:
            res = fetch_page(entity, props, order_prop, is_numeric, last_val=last_val, count=500)
        except Exception as e:
            print(f"[{entity}] Error on page {page}: {e}")
            break

        results = res.get("results", [])
        if not results:
            print(f"[{entity}] No results in payload at page {page}.")
            break

        result_data = results[0].get("result", {}).get("data", {})
        dsr = result_data.get("dsr")
        if not dsr or "DS" not in dsr or not dsr["DS"]:
            print(f"[{entity}] End of data reached at page {page}.")
            break

        ds = dsr["DS"][0]
        value_dicts = ds.get("ValueDicts", {})
        ph = ds.get("PH", [])

        rows = decode_ph(ph, props, value_dicts)
        if not rows:
            print(f"[{entity}] No rows decoded at page {page}.")
            break

        all_rows.extend(rows)
        new_last_val = rows[-1][order_prop]
        print(f"[{entity}] Page {page:<3}: +{len(rows):<3} rows (Total: {len(all_rows):<6}) | Last {order_prop}: {new_last_val}")

        if new_last_val == last_val or len(rows) < 500:
            break
        last_val = new_last_val
        time.sleep(0.05)

    return all_rows


def export_table_csv(filepath, rows, props):
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=props)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="ANP SIPED Power BI Extractor")
    parser.add_argument("--test-connection", action="store_true", help="Test Power BI API connection and return sample record")
    parser.add_argument("--table", type=str, help="Extract specific table (or ALL if omitted)")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save output files")
    args = parser.parse_args()

    if args.test_connection:
        print("Testing Power BI connection...")
        res = fetch_page("DM_SIPED_PROJETO", ["NUM_PROJETO_ANP", "DSC_TITULO"], "NUM_PROJETO_ANP", False, count=5)
        ds = res["results"][0]["result"]["data"]["dsr"]["DS"][0]
        rows = decode_ph(ds.get("PH", []), ["NUM_PROJETO_ANP", "DSC_TITULO"], ds.get("ValueDicts", {}))
        print("Connection successful! Sample decoded rows:")
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        sys.exit(0)

    tables = [args.table] if args.table and args.table in TABLE_SCHEMAS else list(TABLE_SCHEMAS.keys())

    dataset_completo = {}

    for entity in tables:
        config = TABLE_SCHEMAS[entity]
        rows = fetch_entire_table(entity, config)
        dataset_completo[entity] = rows

        csv_path = os.path.join(args.output_dir, config["csv_filename"])
        export_table_csv(csv_path, rows, config["props"])
        print(f"Saved {len(rows)} rows to CSV: {csv_path}")

    json_path = os.path.join(args.output_dir, "siped_dataset_completo.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset_completo, f, ensure_ascii=False, indent=2)
    print(f"\nSaved complete dataset JSON to: {json_path}")


if __name__ == "__main__":
    main()
