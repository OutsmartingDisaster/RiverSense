#!/bin/bash
sed -i '8s/.*/from database.models import GNSSData, Base/' /app/api/main.py
sed -i '9s/.*/from database.session import get_db_session, engine/' /app/api/main.py