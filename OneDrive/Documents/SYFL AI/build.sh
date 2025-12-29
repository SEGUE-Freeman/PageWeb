#!/usr/bin/env bash
# Script de build pour Render

# Installer les dépendances
pip install -r requirements.txt

# Exécuter les migrations Alembic
alembic upgrade head
