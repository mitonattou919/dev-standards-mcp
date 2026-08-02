---
name: coauthoring-standards
description: 実践知を開発標準ナレッジ（sample-knowledge）へ書き起こす／既存文書を更新し、PRまで作成する。「実践知を書き戻す」「ナレッジに追加」「標準を追加・更新したい」と言われたとき、または concept-001 の循環ステップ5を実行するときに使う。
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run ruff check *), Bash(uv run mypy *), Bash(uv run pytest *), Bash(uv run pip-audit *), Bash(grep *), Bash(git status *), Bash(git branch *), Bash(git diff *), Bash(git rev-parse *), Bash(git checkout main), Bash(git checkout -b *), Bash(git pull --ff-only), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(gh pr create *)
---

# 開発標準ナレッジの共同執筆

`sample-knowledge/` 配下へOKF Profile準拠の文書を追加・更新し、PRを作成する。

`concept-001`（エージェント駆動開発の実践知循環）の**ステップ5「得られた知見を書き戻す」**を実行するための手順である。

## 前提

このスキルは dev-standards-mcp リポジトリ内でのみ起動する。他リポジトリ（#30 のOTel計測基盤等）での作業中に得た知見を書き戻す場合は、**知見の出所を入力として受け取る**（手順1）。

書き戻すかどうかの最終判断は人間が行う。エージェントが勝手に標準を制定しない。

## 手順

### 0. 作業ブランチを用意する（何かを編集する前に必ず行う）

**編集を始めてからブランチを切らない。** 起動時点のブランチが `main` でなかった場合、そのブランチの未マージコミットを丸ごと含んだPRになる。

まず現在の状態を確認する。

```bash
git branch --show-current
git status --short
```

判断せずユーザーへ確認するのは次の2つ。**勝手に stash / commit / 破棄しない。**

| 状況 | 対応 |
|------|------|
| 未コミットの変更がある | 変更内容を提示し、どう扱うか確認する。このスキルの成果物へ混ぜてよいものかは人間しか判断できない |
| 現在のブランチが `main` でない | 既存ブランチの続きとして書くのか、`main` から新しく切るのか確認する |

確認がとれたら `main` を基点に作業ブランチを作る。

```bash
git checkout main
git pull --ff-only
git checkout -b docs/<内容を表すスラッグ>
```

### 1. 入力を確認する

以下が揃っていなければユーザーへ聞く。**推測で埋めない**。

| 項目 | 内容 |
|------|------|
| 知見の内容 | 何が分かったか。何に困ったか |
| 出所 | どのリポジトリ・どの作業で得たか。可能ならコミットSHAやPR番号 |
| 一般化の範囲 | この1プロジェクト限りの話か、他プロジェクトにも効くか |

**出所が「今回の作業そのもの」の場合も明示的に記録する。** 後から観測ログとして追跡できなくなるため。

ここで聞いた出所は、手順6で**文書本文の `## 由来` 節へ必ず書き残す**。聞くだけで成果物に残さない状態で完了しない。

### 2. 既存文書を検索して重複を避ける

新規作成の前に、必ず既存文書を検索する。

以下の `uv run python -c` は任意コードの実行にあたるため、`allowed-tools` で事前承認していない。実行のたびにユーザーの承認を求めること（承認を避けるためにスニペットを書き換えない）。

```bash
uv run python -c "
import asyncio
from fastmcp.tools import FunctionTool
from src.api.server import create_server

mcp = create_server()

async def run():
    tool = await mcp.get_tool('search_standards')
    assert isinstance(tool, FunctionTool)
    return tool.fn(query='<検索語>')

for r in asyncio.run(run()):
    print(r.id, r.title, r.score)
"
```

検索は FTS5 の `tokenize='trigram'` によるフレーズ一致である。**空白区切りの複合語は0件になる**（例: `実践知 循環` → 0件、`実践知循環` → ヒット）。単語を連結した3文字以上のクエリを複数回試すこと。

既存文書に重なる記述があれば、新規作成ではなく**その文書の更新**を提案する。ナレッジの重複は循環を壊す。

### 3. type と配置先を決める

| type | 配置先 | 使いどころ |
|------|--------|-----------|
| `standard` | `standards/` | 遵守を求めるルール。`rule_level` が必要 |
| `guideline` | `guidelines/` | 推奨する進め方。強制はしない |
| `checklist` | `checklists/` | 確認項目の列挙 |
| `template` | `templates/` | 雛形 |
| `concept` | `concepts/` | 考え方・モデル・用語の定義 |
| `example` | `examples/` | 具体例 |
| `reference` | （索引用。新規作成しない） | `index.md` のみ |
| `decision` / `howto` / `exception` | 未使用 | 使う前に人間へ確認する。CONTEXT.md の未決事項 |

**`standard` を選ぶのは慎重に。** 実践1回で得た知見はまず `guideline` か `concept` から始め、複数回の実践を経てから昇格させる。

### 4. IDを採番する

`{type}-{連番3桁}`。prefix は `type` と一致させる。

```bash
grep -rh "^id: " sample-knowledge/ | sort
```

同じ type の最大連番 + 1 を採る。

**既知の例外**: `glossary-001` は `type: concept` だが Phase 1 期の例外としてID・配置ともに維持する。これを前例として広げない（`docs/CONTEXT.md` Phase 1.5-5 決定事項3）。

### 5. フロントマターを埋める

全typeで必須。

```yaml
type:    # 手順3で決めたもの
id:      # 手順4で採番したもの
title:   # 文書の名前
summary: # 1文。検索結果に表示されるため、何の文書か分かる粒度で書く
status:  # 下記参照
owner:   # 既存文書に合わせるなら platform-team
tags:    # リスト形式。検索の手がかりになる語を2〜4個
```

`type: standard` のみ追加で必須。1つでも欠けるとパースが失敗する。

```yaml
rule_level:     # must | should | may | reference
technologies:   # リスト。空リストは「未設定」として弾かれる
applies_to:     # リスト。全体に効くなら [all-projects]
version:        # 文字列。"1.0.0" のようにクォートする
effective_date: # YYYY-MM-DD
```

#### status の選び方

| 値 | 条件 |
|----|------|
| `draft` | **実践による検証を経ていない。新規作成時は原則これ** |
| `active` | 実践で使われ、有効と確認できたもの |

`draft` で始めることを恐れない。検証前の文書を `active` にすると、検証していない設計まで規範化される（#34 の判断）。

### 6. 本文を書く

- 冒頭に `# {title}` を置く
- `draft` の場合、最初の節でその旨と、何を検証したいのかを書く
- 決定した内容だけでなく、**なぜそう決めたか**を残す。後から覆すときに必要になる
- 現時点で意図的に決めていないことがあれば、末尾に明示する

#### `## 由来` 節（新規作成時は必須）

手順1で確認した出所を、本文末尾の固定セクションへ書く。PR本文のevidenceはPRにしか残らないため、**文書自体が出所を持つ**ようにする。

```markdown
## 由来

- 出所: <リポジトリ名> / <PR番号・Issue番号・コミットSHA のいずれか>
- 得られた作業: <何をしていて分かったか>
- 一般化の範囲: <この1プロジェクト限りか、他プロジェクトにも効くか>
```

出所が本リポジトリ自身の作業である場合も省略しない。既存文書を更新した場合は、この節へ追記する（過去の出所を消さない）。

### 7. index.md を更新する

`sample-knowledge/index.md` の該当節へ追記する。節が無ければ新設する。並び順は既存の type 順に合わせる。

```markdown
## concepts

- [concept-001: エージェント駆動開発の実践知循環](./concepts/concept-001.md)
```

新しいディレクトリを作った場合は `AGENTS.md`（`CLAUDE.md` はこれへのシンボリックリンク）のディレクトリ構成も更新する。

### 8. 検証する

CLAUDE.md の Definition of Done は文書のみの変更でも適用される。4つすべて実行する。

```bash
uv run ruff check .
uv run mypy .
uv run pytest
uv run pip-audit
```

パースエラー・重複IDは `pytest` で落ちる。

そのうえで、書いた文書がMCP Tool経由で引けることを確認する。**`get_standard` の戻り値はMarkdown本文の文字列であり、`search_standards` の戻り値（`id` / `title` / `score` を持つオブジェクトのリスト）とは型が違う。** 手順2のスニペットを流用せず、以下をそのまま使う。

```bash
uv run python -c "
import asyncio
from fastmcp.tools import FunctionTool
from src.api.server import create_server

mcp = create_server()

async def run():
    tool = await mcp.get_tool('get_standard')
    assert isinstance(tool, FunctionTool)
    return tool.fn(id='<書いた文書のID>')

print(asyncio.run(run())[:400])
"
```

**テストが文書の件数を固定するアサーションを持っていないか確認する。** `assert len(documents) == N` の類は文書追加のたびに壊れるだけで、守りたい仕様ではない。見つけたら代表IDの探索確認へ書き換える（#34 で `test_okf_parser.py` と `test_index_builder.py` の2箇所を修正済み）。

### 9. 決定をCONTEXT.mdへ記録する

新しいディレクトリの新設・ID規則の変更・type の初使用など、**後から「なぜそうなっているか」を問われる判断**をした場合は `docs/CONTEXT.md` へ記録する。暗黙の判断で既成事実にしない。

### 10. PRを作る

外部スキルへ依存せず、本手順だけで完結させる（`github-flow` は本リポジトリに同梱されていないため、cloneしただけの環境では実行できない）。

ブランチは手順0で作成済み。**`git add -A` を使わない。** 起動前から存在する無関係な変更まで巻き込むため、書いたファイルを明示的に指定する。

```bash
git add sample-knowledge/ docs/CONTEXT.md   # 実際に書いたパスだけを列挙する
git status --short                          # ステージ漏れ・混入がないか
git diff --cached                           # コミットする差分そのものを読む
```

差分を確認してからコミットする。

```bash
git commit -m "<件名>" -m "<本文>"           # 本文にはなぜ書き戻すのかを残す
git push -u origin HEAD
git rev-parse HEAD                          # evidence へ書くコミットSHA
gh pr create --title "<タイトル>" --body-file <本文を書いたファイル>
```

コミットメッセージは `standard-002`（コミットメッセージ規約）に、PR説明文は `template-001` に従う。書く前に両方を取得すること（手順8のスニペットに `id` を渡すか、`sample-knowledge/` 配下を直接読む。どちらで取得したかは evidence の `参照方式` に記録する）。

PR本文には `concept-001` の evidence フォーマットを記載する。

```yaml
参照:
  dev_standards_commit: <コミットSHA>
  working_tree: clean | dirty
  参照方式: mcp | direct-skill | bootstrap
  参照文書: [<参照した文書ID>]
適用:
  - 文書ID: <ID>
    適用箇所: <ファイル・該当箇所>
    実行した検証: <コマンド>
    結果: 準拠 | 逸脱
適用不能・逸脱:
  - 文書ID: <ID>
    項目: <項目>
    理由: <理由>
```

`参照方式` は3値のみ。dev-standards-mcp 自身の作業なので通常は `bootstrap` になる。自由記述しない。

## やってはいけないこと

- 実践1回の知見をいきなり `type: standard` / `rule_level: must` にする
- 検証前の文書を `status: active` にする
- 既存文書を検索せずに新規作成する
- 出所を聞くだけで、本文の `## 由来` 節へ残さずに完了する
- `type` と一致しないIDを新たに採番する
- DoD（ruff / mypy / pytest / pip-audit）を一部だけ実行してPRを作る
- `main` へ直接コミットする
- 編集を始めてからブランチを切る（手順0を飛ばす）
- `git add -A` で一括ステージする
- 起動前から存在するユーザーの未コミット変更を、確認せず stash / commit / 破棄する
- 「実行できなかったこと」を書かずに完了報告する
