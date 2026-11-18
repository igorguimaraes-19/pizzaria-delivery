"""Ponto de entrada. Local: `python run.py`. Produção: `gunicorn run:app`."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
