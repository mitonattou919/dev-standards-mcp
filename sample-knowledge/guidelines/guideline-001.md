---
type: guideline
id: guideline-001
title: Python開発ツールガイド（uv / Ruff / mypy / poethepoet / pre-commit）
summary: uv・Ruff・mypy・poethepoet・pre-commitの役割分担と設定例をまとめた実践ガイド。
status: active
owner: platform-team
tags:
  - python
  - uv
  - ruff
  - mypy
---

# L2: Python開発環境のセットアップ

## このドキュメントについて

AIと一緒にPythonを書くための実践ガイド。
「このツールを使え」ではなく「なぜこれを選んだか」という観点から書いている。

## 1. ツール概要

4つの役割を、それぞれ専用ツールに割り当てる。

| 役割 | ツール |
|---|---|
| 環境・依存関係管理 | `uv` |
| Lint・フォーマット | `Ruff` |
| 型チェック | `mypy` |
| タスクランナー | `poethepoet` |

各ツールが一つのことをうまくやる構成にしている。責務を分割したほうが、一つのツールに全部詰め込むより速く、壊れにくい。

## 2. uv — 環境・依存関係管理

`pip` + `pyenv` + `pip-tools` を個別に運用する時代は終わった。`uv`に統合する。

**なぜuvなのか**

- Rust製で圧倒的に高速（待ち時間がほぼゼロ）
- Pythonバージョン管理・仮想環境・パッケージ管理を一つでまかなえる
- `uv.lock`にPythonバージョンとOSレベルのバイナリまで記録されるため、「自分の環境では動く」問題がほぼ起きない

**基本コマンド**

```bash
uv python install 3.13        # Pythonバージョンをインストール
uv init --python 3.13         # プロジェクトを作成
uv sync                       # 環境をuv.lockの状態に同期
uv add {package}              # 依存関係を追加
uv run {command}              # プロジェクトの仮想環境でコマンドを実行
```

`uv.lock`はコミットすること。これが正本の環境の記録になる。

## 3. Ruff — Lint・フォーマット

`Flake8`と`Black`をRuff一つに置き換える。こちらもRust製でミリ秒オーダーで完了する。

**2つの役割**

- **Lint（`ruff check`）**: 未使用importや`None`との`==`比較、未使用変数など、論理的なミスを検出する
- **Format（`ruff format`）**: クォートスタイル、インデント、スペースなど見た目を統一する

**`pyproject.toml`の設定例**

```toml
[tool.ruff]
select = ["E", "F", "UP", "B"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

`--fix`フラグで自動修正できるものは自動修正し、PRの差分をきれいに保つ。

## 4. mypy — 型チェック

型ヒントを書き、`mypy`で静的解析する。「動くかどうか」だけでなく「型として正しいか」を実行前に確認する。

**なぜ必要か**

Pythonは型が間違っていても実行時にエラーにならないことがある。例えば以下のようなコード。

```python
def repeat_message(message: str, times: int) -> str:
    return message * times

repeat_message(3, 4)  # Pythonは実行してしまうが、mypyは止める
```

AIが生成したコードは型がゆるくなりがちだ。`mypy`を実行することで「動くが壊れている」コードを減らせる。

**実行**

```bash
uv run mypy .  # ディレクトリ全体をチェック（単一ファイルのチェックではモジュール横断の問題を見逃す）
```

## 5. poethepoet — タスクランナー

lint・format・型チェックのコマンドを`poe`にまとめておけば、いちいち覚える必要がなくなる。

**`pyproject.toml`の設定例**

```toml
[tool.poe.tasks]
format     = "uv run ruff format ."
lint       = "uv run ruff check --fix ."
type-check = "uv run mypy ."
check      = ["format", "lint", "type-check"]  # まとめて実行
```

`uv run poe check`で「format → lint → 型チェック」を順番に実行する。最初の型エラーで止まる。

## 6. pre-commit — コミット前の自動チェック

`poe check`をpre-commitフックに組み込めば、`git commit`のたびに品質チェックが自動で走る。

**`.pre-commit-config.yaml`**

```yaml
repos:
  - repo: local
    hooks:
      - id: poe-check
        name: poe-check
        entry: uv run poe check
        language: system
        types: [python]
```

ポイントは`language: system`を使うこと。フックがプロジェクトの`uv`環境を使うため、フックと開発環境の間でバージョンのずれが起きない。

問題があればコミットはブロックされる。あとでまとめて直すより、その場で直すほうがいい。

## クイックリファレンス

| やること | コマンド | タイミング |
|---|---|---|
| 環境同期 | `uv sync` | 依存関係が変わったとき |
| Lint＋自動修正 | `uv run ruff check --fix .` | コード変更後 |
| フォーマット | `uv run ruff format .` | コード変更後 |
| 型チェック | `uv run mypy .` | コード変更後 |
| 全チェック実行 | `uv run poe check` | コミット前 |
| （自動）pre-commitチェック | `git commit` | pre-commitが自動実行 |

出典: [mitonattou919/engineering-with-ai](https://github.com/mitonattou919/engineering-with-ai/blob/main/L2-practices/guide-python-dev.md)
