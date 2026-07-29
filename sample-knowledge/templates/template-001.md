---
type: template
id: template-001
title: PR説明文テンプレート
summary: プルリクエスト作成時に使う説明文の雛形。Summary/Test planの2セクション構成。
status: active
owner: platform-team
tags:
  - pull-request
  - template
---

# PR説明文テンプレート

```markdown
## Summary
- 変更点を1〜3個の箇条書きで

## Test plan
- [ ] 実行したテストコマンド
- [ ] 手動確認した内容
```

## 使い方

- Summaryは「何を変更したか」ではなく「なぜ変更したか」を書く
- Test planはレビュアーが再現できる粒度で書く
