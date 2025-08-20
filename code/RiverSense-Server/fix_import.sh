#!/bin/bash
sed -i "s/from database.models import GNSSData, get_db_session/from database.models import GNSSData, Base\nfrom database.session import get_db_session, engine/" /app/api/main.py