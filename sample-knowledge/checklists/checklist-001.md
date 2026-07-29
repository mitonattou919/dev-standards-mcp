---
type: checklist
id: checklist-001
title: PRレビュー基本チェックリスト
summary: プルリクエストをレビュー・マージする前に確認する基本項目のチェックリスト。
status: active
owner: platform-team
tags:
  - review
  - pull-request
---

# PRレビュー基本チェックリスト

## 自動チェック

- [ ] `uv run ruff check .` が通っている
- [ ] `uv run mypy .`（strictモード）が通っている
- [ ] `uv run pytest` が全件パスしている
- [ ] テストカバレッジが閾値（70%）を超えている

## コードレビュー観点

- [ ] 変更の目的がPR説明文に書かれている（「何を」ではなく「なぜ」）
- [ ] 不要な抽象化・過剰な汎用化が無い
- [ ] エラーハンドリングが必要な箇所にだけ入っている
- [ ] テストが正常系・異常系の両方をカバーしている

## マージ前の確認

- [ ] 対象イシューが`Closes #xxx`で紐付いている
- [ ] direct pushではなくPR経由である
