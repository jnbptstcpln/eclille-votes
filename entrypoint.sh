#!/bin/sh
set -e

# Les migrations ne sont pas générées par ce script : elles doivent être dans le dépôt.
# Sans elles, "migrate" ne créerait pas les tables des apps ci-dessous.
for app in cla_auth cla_bdx cla_ca cla_enscl cla_customvotes; do
    if [ ! -d "$app/migrations" ]; then
        echo "ERREUR : $app/migrations est absent du dépôt (récupère-le depuis le serveur OVH et commite-le)." >&2
        exit 1
    fi
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn cla_votes.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
