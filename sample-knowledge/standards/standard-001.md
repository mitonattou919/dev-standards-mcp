---
type: standard
id: standard-001
title: Azureリソースネーミング規約
summary: Azureリソースの命名パターンと必須タグを定めた規約。CAFの略語一覧をベースに、環境・workloadを名前に含める。
status: active
owner: platform-team
tags:
  - azure
  - naming
  - tagging
rule_level: must
technologies:
  - azure
applies_to:
  - all-projects
version: "1.0.0"
effective_date: 2026-07-29
---

# Azure リソース規約

## このドキュメントについて

Azure リソースの命名とタグ付けを一貫して行うための実践ガイド。
「このルールを使え」ではなく「なぜこう決めたか」から書く。

## 1. リソースネーミング

### パターン

```
{type}-{workload}-{env}-{instance}
```

| コンポーネント | 説明                                       | 例                          |
|--------------|--------------------------------------------|-----------------------------|
| `type`       | CAF のリソース略語                          | `rg`, `vm`, `kv`            |
| `workload`   | **3文字固定の略語**（サービスの識別子）       | `api`, `web`, `mng`, `bat`  |
| `env`        | 環境 — **3文字固定**                        | `prd`, `stg`, `dev`         |
| `instance`   | ゼロパディングの連番                         | `001`, `002`                |

**リージョンを含めない理由:** リソースはサブスクリプション単位でデプロイされ、リージョン情報はタグや Azure のメタデータで管理する。グローバルリソース（Front Door、DNS ゾーンなど）にはリージョンの概念がなく、DR ペアも名前ではなく論理単位として扱う。

**環境を含める理由:** サブスクリプションは環境ごとに分離しているが、stg と dev が同一サブスクリプションに混在するケースもあり得る。環境をリソース名に含めることで、サブスクリプションのコンテキストに依存せず名前だけで判断できる。

### workload 略語の設計ルール

workload セグメントは **必ず3文字** にする。

- 用途が直感的に連想できる略語を選ぶ（例: `api`, `web`, `mng`, `bat`, `ctl`）
- プロジェクト内で**一意**にする（同じ略語の重複は禁止）
- 正式名称は `Project` タグで補足する（後述の[タグ](#2-タグ)を参照）

> **なぜ3文字？** リソース種別ごとに文字数制限が異なる中でも読みやすさを保てる短さで、かつ一目で区別できる長さ。

### 命名例

| リソース             | 名前                  | 備考                                    |
|---------------------|----------------------|-----------------------------------------|
| リソースグループ      | `rg-mng-prd-001`     |                                         |
| 仮想マシン           | `vm-mng-prd-001`     |                                         |
| ストレージアカウント   | `stmngprd001`        | ハイフン不可・小文字のみ（Azure の制約）  |
| Key Vault           | `kv-mng-prd-001`     |                                         |
| App Service         | `app-api-prd-001`    |                                         |
| App Service Plan    | `asp-api-prd-001`    |                                         |

### リソース種別の略語

CAF 公式の略語一覧に従う:
https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations

## 2. タグ

### 必須タグ

全リソースに以下の3つのタグを付与する。

| キー           | 形式                        | 例                           | 目的                                                |
|---------------|----------------------------|------------------------------|----------------------------------------------------|
| `Environment` | `prd` / `stg` / `dev`      | `prd`                        | デプロイ環境の区分                                   |
| `Owner`       | チーム名またはメールアドレス   | `team-platform`              | リソースの責任者                                     |
| `Project`     | `{workload}: {正式名称}`    | `mng: Management Platform`   | 3文字の workload 略語を人間が読める形で補足する        |

`Project` タグは、略語テーブルを暗記しなくても誰でもリソースの用途を理解できるようにするための補足。

### 任意タグ

必要に応じて追加する。

| キー          | 例              | 目的                        |
|--------------|-----------------|----------------------------|
| `CostCenter` | `cc-1234`       | コスト配分・請求先の管理      |
| `ManagedBy`  | `terraform`     | リソースのプロビジョニング方法 |

## クイックリファレンス

| 項目                  | ルール                                                                |
|----------------------|----------------------------------------------------------------------|
| 命名パターン           | `{type}-{workload}-{env}-{instance}`                                 |
| workload セグメント    | 3文字固定、プロジェクト内で一意、用途が連想できること                    |
| env セグメント         | `prd` / `stg` / `dev`                                                |
| ストレージアカウント    | ハイフン不可 — 各コンポーネントを連結、小文字のみ                        |
| 必須タグ              | `Environment`, `Owner`, `Project`                                    |

出典: [mitonattou919/engineering-with-ai](https://github.com/mitonattou919/engineering-with-ai/blob/main/L2-practices/guide-azure.ja.md)
