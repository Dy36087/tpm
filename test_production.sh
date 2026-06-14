#!/bin/bash
# Script para testar deploy localmente com variáveis de ambiente

# Carregar variáveis de .env.local se existir
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '#' | xargs)
fi

echo "🔧 Testando setup de produção localmente..."
echo "DEBUG: $DJANGO_DEBUG"
echo "SECRET_KEY: ${DJANGO_SECRET_KEY:0:10}..."
echo "ALLOWED_HOSTS: $DJANGO_ALLOWED_HOSTS"

# Executar migrations
echo "📦 Rodando migrations..."
python manage.py migrate

# Coletar static files
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executar com gunicorn (como faria em produção)
echo "🚀 Iniciando com Gunicorn (acesse http://127.0.0.1:8000)..."
gunicorn ptm.wsgi --bind 0.0.0.0:8000 --log-file -
