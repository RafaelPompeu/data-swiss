# DataSwiss

DataSwiss é um conjunto de ferramentas web para facilitar tarefas comuns de dados, como formatação de JSON e SQL.

## Funcionalidades

- **Formatador JSON:** Cole seu JSON e obtenha uma versão formatada e legível.
- **Formatador SQL:** Cole sua query SQL e veja o código organizado automaticamente.
- **Interpretador Cron:** Monte e interprete expressões cron facilmente.
- **Visualizador Parquet:** Faça upload de um arquivo Parquet, visualize as 10 primeiras linhas, veja o dicionário de dados (nome, tipo, count) e gere um gráfico de frequência (top 30) de qualquer coluna.

## Como rodar localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/RafaelPompeu/data-swiss.git
   cd data-swiss
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o servidor Flask:**
   ```bash
   python app.py
   ```
   Ou, se preferir:
   ```bash
   export FLASK_APP=app:create_app
   flask run
   ```

5. **Acesse no navegador:**
   ```
   http://localhost:5000
   ```

## Estrutura do Projeto

```
data-swiss/
├── app.py
├── app/
│   ├── __init__.py
│   └── routes.py
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── json_formatter.html
│   └── sql_formatter.html
├── requirements.txt
└── README.md
```

## Links

- [GitHub](https://github.com/RafaelPompeu/data-swiss)
- [LinkedIn](https://www.linkedin.com/in/rafael-pompeu-p/)

---

Feito com ❤️ por Rafael Pompeu.
