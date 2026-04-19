# minilog

APIが使えるミニブログ。テキスト+写真の投稿をAPI経由で管理。公開設定で外部からの閲覧も可能。

## 特徴

- JWT認証によるマルチユーザー対応
- テキスト+複数写真の投稿（サムネイル自動生成）
- 投稿の公開/非公開切替
- 日付フィルタ・ページネーション
- Swagger UI (`/docs`) で対話的にAPI操作

## デプロイ

mainへのpushで2系統が自動デプロイされる。

```
Gitea push
  ├─ Woodpecker CI → lint/typecheck/test → build & push → .100 デプロイ
  │   minilog.honya.dev (Traefik経由)
  │
  └─ ミラー → GitHub → GitHub Actions → test → rsync + SSH → GCE デプロイ
      /opt/minilog/ (docker compose --build)
```

- **NAS (.100)**: `docker-compose@minilog` (systemd) / bridge + Traefik labels / データは `/mnt/8TBHDD/SERVICES/minilog/`
- **GCE**: `/opt/minilog/` に rsync → `docker compose up -d --build`

### ローカル開発

```bash
cp .env.example .env
# JWT_SECRET を変更
uvicorn src.app.main:app --reload --port 8000
```

`http://localhost:8000/docs` でSwagger UIが開く。

### テスト

```bash
python -m pytest tests/ -v
```

## API

すべてのエンドポイントは `/api/v1` 以下。

### 認証

| メソッド | パス             | 説明                              |
| -------- | ---------------- | --------------------------------- |
| POST     | `/auth/register` | ユーザー登録                      |
| POST     | `/auth/login`    | ログイン（JWTトークン取得）       |
| GET      | `/auth/me`       | アカウント情報取得                |
| PUT      | `/auth/me`       | アカウント設定変更（公開/非公開） |

### 投稿（要認証）

| メソッド | パス             | 説明                                                |
| -------- | ---------------- | --------------------------------------------------- |
| POST     | `/entries`       | 投稿作成（multipart: text + entry_date + photos[]） |
| GET      | `/entries`       | 一覧取得（?date_from, ?date_to, ?offset, ?limit）   |
| GET      | `/entries/dates` | 投稿がある日付一覧（?year, ?month）                 |
| GET      | `/entries/{id}`  | 投稿詳細                                            |
| PUT      | `/entries/{id}`  | 投稿更新（text, entry_date, is_public）             |
| DELETE   | `/entries/{id}`  | 投稿削除                                            |

### 写真（要認証）

| メソッド | パス                        | 説明                         |
| -------- | --------------------------- | ---------------------------- |
| POST     | `/entries/{id}/photos`      | 写真追加                     |
| GET      | `/photos/{id}/image?token=` | 写真取得（?w= でサムネイル） |
| DELETE   | `/photos/{id}`              | 写真削除                     |

### 公開API（認証不要）

| メソッド | パス                        | 説明                                            |
| -------- | --------------------------- | ----------------------------------------------- |
| GET      | `/public/entries`           | 公開投稿一覧（?username, ?date_from, ?date_to） |
| GET      | `/public/entries/dates`     | 公開投稿の日付一覧（?username, ?year, ?month）  |
| GET      | `/public/entries/{id}`      | 公開投稿詳細                                    |
| GET      | `/public/photos/{id}/image` | 公開写真取得（?w= でサムネイル）                |

## 技術スタック

- Python 3.13 / FastAPI / SQLAlchemy (async) / SQLite
- JWT認証 / Alembic マイグレーション
- Docker Compose デプロイ / Woodpecker CI
