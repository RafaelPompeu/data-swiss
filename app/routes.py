from flask import Blueprint, render_template, request, flash
import json
import sqlparse

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