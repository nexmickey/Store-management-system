# Generate migration script
docker exec -it iepcourierproject-auth-app-1 flask --app source/migrate.py db migrate -m "Added dummy"

# Apply changes to database
docker exec -it iepcourierproject-auth-app-1 flask --app source/migrate.py db upgrade
