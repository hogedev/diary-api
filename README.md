# diary-api

汎用日記API。写真+テキストの個別投稿を日付でグルーピングして管理。

## 開発

```bash
uvicorn src.app.main:app --reload --port 8000
```

## テスト

```bash
python -m pytest tests/ -v
```

## API

- `POST /api/v1/entries` - 投稿作成（multipart: text + entry_date + photos[]）
- `GET /api/v1/entries` - 一覧（?date_from, ?date_to, ?offset, ?limit）
- `GET /api/v1/entries/dates` - 投稿がある日付一覧
- `GET /api/v1/entries/{id}` - 詳細
- `PUT /api/v1/entries/{id}` - 更新
- `DELETE /api/v1/entries/{id}` - 削除
- `POST /api/v1/entries/{id}/photos` - 写真追加
- `GET /api/v1/photos/{id}/image` - 写真取得（?w= でサムネイル）
- `DELETE /api/v1/photos/{id}` - 写真削除
