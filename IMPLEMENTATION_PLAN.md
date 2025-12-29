# 実装計画と技術スタック

## 1. 概要
### 1.1 システム概要
本システムは、入力されたテキストに対してLLM（大規模言語モデル）を用いて矛盾を検出し、該当箇所を構造化されたデータとして出力するシステムである。

### 1.2 目的
- テキスト内に存在する事実の矛盾（人物名、日付、数値、属性など）を自動検出する
- 検出結果を型安全な構造化データとして取得し、後続処理（UI表示、ログ保存など）に活用可能にする
- Pydanticモデルを活用することで、出力フォーマットの一元管理とLLMへの指示を自動生成する

## 2. 実装順序
1. 要件整理と入出力仕様の確定
   - 矛盾の定義、検出対象、入力テキストの形式
   - 出力スキーマ（Pydanticモデル）の設計
2. コア検出ロジック（LLM連携）
   - プロンプト設計
   - LLM出力の構造化とバリデーション
   - LLMオーケストレーション（LangChain）
3. API層の実装
   - 検出リクエスト/レスポンスのエンドポイント設計
   - 入出力スキーマのバリデーション
4. UI/可視化（本番運用を想定したUIを作成）
   - 入力テキスト編集と実行フロー
   - 矛盾箇所のハイライト
   - 結果の一覧表示とフィルタ
5. 評価・テスト
   - 代表的なサンプルデータ作成
   - テストケースと評価指標の整備
6. ログ/監査/運用
   - 検出結果の保存
   - 失敗時のリトライと監視

## 3. 出力スキーマ設計案
- 設計方針: subject + attribute に対して相反する claims を束ねる
- UI連携: evidence にテキスト内位置（start/end）を持たせ、ハイライト可能にする
- 型安全: type や value_type を Literal で固定し、後続処理の分岐を明確化
- 正規化: 日付/数値は value_normalized を持ち、比較や集計に利用

### 3.1 Pydanticモデル（案）
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class EvidenceSpan(BaseModel):
    start: int = Field(..., description="0-based start")
    end: int = Field(..., description="0-based end (exclusive)")
    text: str

class Claim(BaseModel):
    value_text: str
    value_type: Literal["date", "number", "string", "other"]
    value_normalized: str
    evidence: list[EvidenceSpan]

class Entity(BaseModel):
    text: str
    normalized: Optional[str] = None
    entity_type: Literal["person", "org", "location", "event", "other"]

class Contradiction(BaseModel):
    id: str
    type: Literal["attribute_conflict", "date_mismatch", "number_mismatch", "name_mismatch"]
    subject: Entity
    attribute: str
    claims: list[Claim]
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class ContradictionResult(BaseModel):
    document_id: Optional[str] = None
    contradictions: list[Contradiction]
```

### 3.2 サンプル出力（案）
```json
{
  "document_id": "doc-001",
  "contradictions": [
    {
      "id": "c1",
      "type": "date_mismatch",
      "subject": { "text": "A男", "normalized": "A男", "entity_type": "person" },
      "attribute": "誕生日",
      "claims": [
        {
          "value_text": "10月22日",
          "value_type": "date",
          "value_normalized": "10-22",
          "evidence": [{ "start": 5, "end": 13, "text": "A男の誕生日は10月22日" }]
        },
        {
          "value_text": "4月5日",
          "value_type": "date",
          "value_normalized": "04-05",
          "evidence": [{ "start": 25, "end": 32, "text": "A男の誕生日は4月5日" }]
        }
      ],
      "explanation": "同一人物の誕生日が2つの異なる日付で記述されている",
      "confidence": 0.92
    }
  ]
}
```

## 4. UI方針（詳細）
- 画面構成: 入力編集 → 実行 → 結果表示の3ペイン
- 主要機能: テキスト入力、実行ボタン、矛盾の一覧、本文ハイライト
- 表示戦略: 矛盾ごとに subject/attribute/claims をカード表示
- フィルタ: type、confidence、subject で絞り込み
- エクスポート: JSONダウンロード（検証/ログ用途）
- エラーハンドリング: LLM失敗時のリトライと手動再実行

## 5. 技術スタック
- 言語: Python 3.11+
- 仮想環境/パッケージ管理: uv
- 型/スキーマ: Pydantic v2
- LLM連携: OpenAI API（または互換API）
- LLMオーケストレーション: LangChain
- 実行環境: Docker
- テスト: pytest
- ログ: structlog（または標準logging）
- Lint/Format: ruff
- API: FastAPI
- UI: Next.js (React) + TypeScript + Tailwind CSS
- UI補助: shadcn/ui + Radix UI（コンポーネント基盤）
- 状態管理: TanStack Query（API同期） + Zustand（ローカル）
- バリデーション: Zod（フロント側の入力検証）
