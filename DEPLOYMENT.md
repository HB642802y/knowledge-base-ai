# Mise en ligne du projet

Cette configuration publie l'application avec Docker :

- `frontend` : React/Vite servi par Nginx
- `backend` : FastAPI
- `db` : PostgreSQL
- volumes persistants : documents uploades, index RAG, base PostgreSQL

## 1. Preparer un serveur

Sur un VPS ou serveur de l'etablissement, installe :

```bash
docker
docker compose
```

Ouvre le port `80`.

## 2. Configurer les variables

Copie le fichier d'exemple :

```bash
cp .env.production.example .env.production
```

Modifie ensuite :

```env
POSTGRES_PASSWORD=mot-de-passe-db-fort
INITIAL_ADMIN_PASSWORD=mot-de-passe-admin-fort
OPENAI_API_KEY=ta-cle-openai-si-disponible
PUBLIC_API_URL=/api/v1
ALLOWED_ORIGINS=*
```

Avec cette configuration, une seule URL suffit. Nginx sert le frontend et redirige `/api/` vers le backend.

Si tu veux configurer un domaine HTTPS plus tard, tu peux remplacer :

```env
ALLOWED_ORIGINS=https://ton-domaine
```

## 3. Lancer

```bash
docker compose --env-file .env.production up -d --build
```

Puis ouvrir :

```text
http://IP_DU_SERVEUR/
```

## 4. Connexion initiale

Le backend cree automatiquement le compte admin au demarrage avec :

```env
INITIAL_ADMIN_EMAIL
INITIAL_ADMIN_PASSWORD
```

Ensuite l'admin cree les comptes collaborateurs depuis l'interface.

## 5. Commandes utiles

Voir les logs :

```bash
docker compose --env-file .env.production logs -f
```

Redemarrer :

```bash
docker compose --env-file .env.production restart
```

Arreter :

```bash
docker compose --env-file .env.production down
```
