from flask import Blueprint, render_template, request, flash
import json
import sqlparse
from cron_descriptor import get_description, ExpressionDescriptor
import re
import pandas as pd
import os
import uuid
from flask import send_from_directory

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/json-formatter', methods=['GET', 'POST'])
def json_formatter():
    input_json = ""
    formatted_json = ""
    error = None
    if request.method == 'POST':
        input_json = request.form.get('input_json', '')
        try:
            if input_json.strip():
                parsed_json = json.loads(input_json)
                formatted_json = json.dumps(parsed_json, indent=4, sort_keys=True)
            else:
                error = "Entrada JSON está vazia."
        except json.JSONDecodeError as e:
            error = f"Erro ao decodificar JSON: {e}"
        except Exception as e:
            error = f"Ocorreu um erro inesperado: {e}"

        if error:
            flash(error, 'error')

    return render_template('json_formatter.html', input_json=input_json, formatted_json=formatted_json)

@main_bp.route('/sql-formatter', methods=['GET', 'POST'])
def sql_formatter():
    input_sql = ""
    formatted_sql = ""
    error = None
    if request.method == 'POST':
        input_sql = request.form.get('input_sql', '')
        try:
            if input_sql.strip():
                formatted_sql = sqlparse.format(input_sql, reindent=True, keyword_case='upper')
            else:
                error = "Entrada SQL está vazia."
        except Exception as e:
            error = f"Ocorreu um erro ao formatar SQL: {e}"

        if error:
            flash(error, 'error')

    return render_template('sql_formatter.html', input_sql=input_sql, formatted_sql=formatted_sql)

def traduzir_cron_descricao(desc):
    # Traduções simples
    traducoes = [
        (r"\bEvery minute\b", "A cada minuto"),
        (r"\bEvery hour\b", "A cada hora"),
        (r"\bEvery day\b", "Todos os dias"),
        (r"\bEvery month\b", "Todos os meses"),
        (r"\bEvery year\b", "Todos os anos"),
        (r"\bAt\b", "Às"),
        (r"\bat\b", "às"),
        (r"\bAnd\b", "e"),
        (r"\band\b", "e"),
        (r"\bbetween\b", "entre"),
        (r"\bthrough\b", "até"),
        (r"\bof the month\b", "do mês"),
        (r"\bof\b", "de"),
        (r"\bAM\b", "da manhã"),
        (r"\bPM\b", "da tarde"),
        (r"\bMonday\b", "segunda-feira"),
        (r"\bTuesday\b", "terça-feira"),
        (r"\bWednesday\b", "quarta-feira"),
        (r"\bThursday\b", "quinta-feira"),
        (r"\bFriday\b", "sexta-feira"),
        (r"\bSaturday\b", "sábado"),
        (r"\bSunday\b", "domingo"),
        (r"\bJanuary\b", "janeiro"),
        (r"\bFebruary\b", "fevereiro"),
        (r"\bMarch\b", "março"),
        (r"\bApril\b", "abril"),
        (r"\bMay\b", "maio"),
        (r"\bJune\b", "junho"),
        (r"\bJuly\b", "julho"),
        (r"\bAugust\b", "agosto"),
        (r"\bSeptember\b", "setembro"),
        (r"\bOctober\b", "outubro"),
        (r"\bNovember\b", "novembro"),
        (r"\bDecember\b", "dezembro"),
        (r"\b, ", ", "),
        (r"\.", "."),
    ]

    # Horários tipo 10:00 AM/PM
    def traduzir_horario(match):
        hora, minuto, periodo = match.groups()
        hora = int(hora)
        if periodo == "PM" and hora != 12:
            hora += 12
        elif periodo == "AM" and hora == 12:
            hora = 0
        return f"{hora:02d}:{minuto}"

    desc = re.sub(r'(\d{1,2}):(\d{2}) (AM|PM)', traduzir_horario, desc)

    # Tradução de padrões compostos
    desc = re.sub(r'on day (\d+) of the month', r'no dia \1 do mês', desc)
    desc = re.sub(r'on days? ([\d,-]+) of the month', r'nos dias \1 do mês', desc)
    desc = re.sub(r'on (\d{1,2}):(\d{2})', r'às \1:\2', desc)

    # "only on Monday" -> "somente na segunda-feira"
    desc = re.sub(r'only on ([a-zA-Z-]+)', r'somente na \1', desc)
    # "only on <mês>" ou "only in <mês>" -> "somente em <mês>"
    desc = re.sub(
        r'only (on|in) (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)',
        r'somente em \2', desc, flags=re.IGNORECASE)
    # "only <mês>" -> "somente em <mês>"
    desc = re.sub(
        r'only (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)',
        r'somente em \1', desc, flags=re.IGNORECASE)
    # "only <dia-da-semana>" -> "somente na <dia-da-semana>"
    desc = re.sub(
        r'only (segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo)',
        r'somente na \1', desc, flags=re.IGNORECASE)
    # Remove qualquer "only in" ou "only on" residual (caso não tenha sido traduzido)
    desc = re.sub(r'only (in|on) ([a-zA-Z-]+)', r'somente em \2', desc, flags=re.IGNORECASE)
    desc = re.sub(r'only ([a-zA-Z-]+)', r'somente em \1', desc, flags=re.IGNORECASE)
    # Corrige "somente na em" para "somente em"
    desc = re.sub(r'somente na em', 'somente em', desc)
    desc = re.sub(r'somente na\s+em', 'somente em', desc)
    # Remove "only in <mês>" que não foi traduzido por erro de case
    desc = re.sub(
        r'only in (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)',
        r'somente em \1', desc, flags=re.IGNORECASE)

    # "on <mês>" ou "in <mês>" -> "em <mês>"
    desc = re.sub(
        r'(on|in) (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)',
        r'em \2', desc, flags=re.IGNORECASE)
    # "on <dia-da-semana>" -> "na <dia-da-semana>"
    desc = re.sub(
        r'on (segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo)',
        r'na \1', desc, flags=re.IGNORECASE)

    # Traduções simples
    for padrao, pt in traducoes:
        desc = re.sub(padrao, pt, desc)

    # Ajustes finais para conectores e fluidez
    desc = re.sub(r", e", " e", desc)
    desc = re.sub(r",,", ",", desc)
    desc = re.sub(r"  +", " ", desc)
    desc = desc.strip()

    # Ajuste de pluralização para dias e meses
    desc = re.sub(r"Todos os dia do mês", "Todo dia do mês", desc)
    desc = re.sub(r"Todos os dias do mês", "Todos os dias do mês", desc)
    desc = re.sub(r"Todos os mês", "Todo mês", desc)
    desc = re.sub(r"Todos os meses", "Todos os meses", desc)

    # Ajuste para frases mais naturais
    desc = re.sub(r"Às (\d{2}:\d{2})", r"Às \1", desc)
    desc = re.sub(r"às (\d{2}:\d{2})", r"às \1", desc)
    desc = re.sub(r"(\d{2}:\d{2}) da manhã", r"\1", desc)
    desc = re.sub(r"(\d{2}:\d{2}) da tarde", r"\1", desc)

    # Primeira letra maiúscula
    if desc:
        desc = desc[0].upper() + desc[1:]
    return desc

def validar_campo_cron(valor, campo):
    # Define padrões válidos para cada campo do crontab
    padroes = {
        'minute': r'^[\d\*,\/\-]+$',
        'hour': r'^[\d\*,\/\-]+$',
        'day': r'^[\d\*,\/\-]+$',
        'month': r'^[\d\*,\/\-]+$',
        'weekday': r'^[\d\*,\/\-]+$',
    }
    # Aceita apenas números, *, /, - e ,
    if not re.match(padroes[campo], valor):
        return False
    return True

@main_bp.route('/cron-guru', methods=['GET', 'POST'])
def cron_guru():
    cron_parts = {
        'minute': '',
        'hour': '',
        'day': '',
        'month': '',
        'weekday': ''
    }
    cron_expr = ""
    cron_human = ""
    error = None
    if request.method == 'POST':
        invalido = False
        for part in cron_parts:
            valor = request.form.get(part, '').strip() or '*'
            if not validar_campo_cron(valor, part):
                error = f"Campo '{part.upper()}' contém caracteres inválidos."
                flash(error, 'error')
                invalido = True
            cron_parts[part] = valor
        if invalido:
            return render_template('cron_guru.html', cron_parts=cron_parts, cron_expr="", cron_human="")
        cron_expr = f"{cron_parts['minute']} {cron_parts['hour']} {cron_parts['day']} {cron_parts['month']} {cron_parts['weekday']}"
        try:
            cron_human = ExpressionDescriptor(cron_expr).get_description()
            cron_human = traduzir_cron_descricao(cron_human)
        except Exception as e:
            error = f"Expressão cron inválida: {e}"
            flash(error, 'error')
    return render_template('cron_guru.html', cron_parts=cron_parts, cron_expr=cron_expr, cron_human=cron_human)

@main_bp.route('/parquet', methods=['GET', 'POST'])
def parquet_view():
    table_html = None
    columns = []
    dicionario = []
    freq_data = []
    selected_col = None
    error = None
    total_count = None
    distinct_total = None
    parquet_file_id = None

    if request.method == 'POST':
        file = request.files.get('parquet_file')
        selected_col = request.form.get('selected_col')
        parquet_file_id = request.form.get('parquet_file_id')

        if parquet_file_id:
            # Seleção de coluna: carrega arquivo temporário
            temp_path = os.path.join(UPLOAD_FOLDER, parquet_file_id)
            if os.path.exists(temp_path):
                try:
                    df = pd.read_parquet(temp_path)
                    total_count = len(df)
                    table_html = df.head(10).to_html(classes="parquet-table", index=False)
                    dicionario = [
                        {
                            'col': col,
                            'dtype': str(df[col].dtype),
                            'count': int(df[col].count()),
                            'distinct': int(df[col].nunique(dropna=True))
                        }
                        for col in df.columns
                    ]
                    columns = list(df.columns)
                    if selected_col and selected_col in df.columns:
                        freq = df[selected_col].value_counts(dropna=False).head(30)
                        freq_data = [{'key': str(idx), 'value': int(val)} for idx, val in freq.items()]
                        distinct_total = int(df[selected_col].nunique(dropna=True))
                except Exception as e:
                    error = f"Erro ao ler o arquivo Parquet: {e}"
            else:
                error = "Arquivo temporário não encontrado. Por favor, envie o arquivo novamente."
        elif file and file.filename.endswith('.parquet'):
            # Upload inicial: salva arquivo temporário
            import uuid
            parquet_file_id = str(uuid.uuid4()) + '.parquet'
            temp_path = os.path.join(UPLOAD_FOLDER, parquet_file_id)
            file.save(temp_path)
            try:
                df = pd.read_parquet(temp_path)
                total_count = len(df)
                table_html = df.head(10).to_html(classes="parquet-table", index=False)
                dicionario = [
                    {
                        'col': col,
                        'dtype': str(df[col].dtype),
                        'count': int(df[col].count()),
                        'distinct': int(df[col].nunique(dropna=True))
                    }
                    for col in df.columns
                ]
                columns = list(df.columns)
                if selected_col and selected_col in df.columns:
                    freq = df[selected_col].value_counts(dropna=False).head(30)
                    freq_data = [{'key': str(idx), 'value': int(val)} for idx, val in freq.items()]
                    distinct_total = int(df[selected_col].nunique(dropna=True))
            except Exception as e:
                error = f"Erro ao ler o arquivo Parquet: {e}"
        else:
            error = "Envie um arquivo .parquet válido."
    else:
        # Resetar variáveis no GET para mostrar o formulário
        table_html = None
        columns = []
        dicionario = []
        freq_data = []
        selected_col = None
        error = None
        total_count = None
        distinct_total = None
        parquet_file_id = None

    return render_template(
        'parquet.html',
        table_html=table_html,
        columns=columns,
        dicionario=dicionario,
        freq_data=freq_data,
        selected_col=selected_col,
        error=error,
        total_count=total_count,
        distinct_total=distinct_total,
        parquet_file_id=parquet_file_id
    )