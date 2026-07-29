---
type: guideline
id: guideline-002
title: pytestベストプラクティス
summary: pytestでテストを書く際の実践的な指針。フィクスチャ、パラメータ化、モック、マーカーの使い分け。
status: active
owner: platform-team
tags:
  - python
  - pytest
  - testing
---

# L2: pytestによるテスト

## このドキュメントについて

[pytest](https://docs.pytest.org/)でテストを書くための実践ガイド。
「こうしなければならない」ではなく「始める前に知っておく価値があること」として読んでほしい。

## 1. まずテストを書く

pytestは柔軟すぎるがゆえに、テストを1つも書かないまま「正しい」構成を作り込むのに時間を使ってしまいがちだ。それはたいてい失敗する。

`test_*.py`にただの関数を書くところから始める。フィクスチャもプラグインも設定もいらない。まず動かす。本当に役立つ構成は、面倒に感じた部分から自然に出てくる。

```python
def test_add():
    assert add(1, 2) == 3
```

これで立派なテストだ。ここから始める。

## 2. フィクスチャは繰り返しをなくすためのもの

フィクスチャは設計目標ではなく、繰り返しへの対処法だ。同じセットアップコードを3つのテストで書いていたら、それがフィクスチャを使うタイミングだ。

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice", "role": "member"}

def test_user_display_name(sample_user):
    assert display_name(sample_user) == "Alice"
```

**フィクスチャのスコープに注意**

- `scope="function"`（デフォルト）— テストごとに再生成される。安全で予測しやすい。
- `scope="session"`— テスト実行全体で1回だけ生成される。コストの高いセットアップ（DB接続やモデルのロードなど）に有効だが、テスト間で状態が漏れないか注意が必要。

まずは`function`スコープで始める。遅さが実際に問題になってから、より広いスコープに広げる。

## 3. 複数ケースはパラメータ化する

同じテストロジックを異なる入力で実行したいときは、`@pytest.mark.parametrize`を使うとすっきりする。

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert to_uppercase(input) == expected
```

ほぼ同じテスト関数を3つ書くより、たいていこちらのほうがいい。各ケースが出力に個別に表示されるため、失敗の切り分けもしやすい。

## 4. モックは境界で使う。内部では使わない

モックは、HTTP呼び出しやデータベース、ファイルI/Oなど、外部システムからコードを切り離すのに有効だ。ただし、モックしすぎるとテストが実際の挙動を検証しなくなり、問題になる。

**使える経験則**

コードが「呼び出しているもの」をモックする。コードが「そのものであるもの」をモックしない。

```python
from unittest.mock import patch

def test_fetch_user_calls_api(mock_get):
    with patch("myapp.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"id": 1}
        result = fetch_user(1)
        assert result["id"] == 1
```

3階層も深くモックしている自分に気づいたら、たいていはテスト対象のコードが多くのことをやりすぎているサインだ。

## 5. マーカーでテストを整理する

マーカーを使うと、テストを分類して部分的に実行できる。

```python
@pytest.mark.slow
def test_heavy_computation():
    ...
```

```bash
# slowテスト以外をすべて実行
pytest -m "not slow"
```

警告を避けるため、カスタムマーカーは`pyproject.toml`に登録しておく。

```toml
[tool.pytest.ini_options]
markers = [
    "slow: tests that take a long time",
    "integration: tests that hit external services",
]
```

厳選した少数のマーカーで十分効果がある。分類しすぎないこと。

## 6. pyproject.tomlに設定を集約する

pytestの設定は他のツールと同様に`pyproject.toml`にまとめておく。設定ファイルをこれ以上増やさないため。

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

`--tb=short`は、大量のテキストに埋もれずに失敗を理解できる程度のトレースバックを出してくれる。好みに応じて調整する。

## 次に考えること

基本的なテストスイートが動くようになったら、次に出てくる問いはこのあたりだ。

- 環境変数や設定ファイルに依存するコードはどうテストするか
- `unittest.mock`より`pytest-mock`が向いているのはどんなときか
- 非同期コード（`pytest-asyncio`）のテストはどう構成するか

自分のコードベースで実際に感じた摩擦を起点に、深掘りしていく。

出典: [mitonattou919/engineering-with-ai](https://github.com/mitonattou919/engineering-with-ai/blob/main/L2-practices/guide-pytest.md)
