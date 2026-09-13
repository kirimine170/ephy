# 常駐会話とfeedbackの責任分界

## Status

Accepted

## Context

改訂3の実装依頼により，既存Runtimeの会話・音声・Preference評価・Profileを再利用して，常駐中の指摘を次の会話へ反映する．分散Workerや学習の完成を待たず，単一PC上で使える最小の常駐経路を先に実装する．この設計branchは`origin/main@03859c6`から分離し，既存の共通設計worktreeを変更しない．

## Decision

- Runtimeの既存Wails／InteractionEngineが常駐session，ASR epoch，生成，SpeechUnit，実際のdeliveryを所有する．通常版と専用検証版はlock，Gateway，設定と保存先を分離する．既存Identityは変更しない．
- 利用modeは休止，応答待受，観測，会話参加とする．初回は明示操作でマイクを開始する．観測の許可と能動発話の許可を分け，停止・直接応答を背景候補より優先する．
- Profile層は有限で型付きの継続的な好みの正本を持つ．session上書きはsession内に限定し，現在の明示的な依頼，session設定，継続設定，既存Profile既定値の順で解決する．Identityと記憶共有権限が常に上限となる．
- 単独feedbackはA/Bのvoteと異なるeventとして既存評価のprivate SQLite基盤に保存する．対象発言と実再生区間，保存同意，設定差分，revision，取消来歴を持たせ，永続化と設定変更をtransactionで結ぶ．失敗を保存・適用済みと表示しない．
- 設定反映はモデルの重み更新ではない．単独の正負評価から未評価のA/B pairやSFT正解を作らず，学習同意は既定で無効とする．事実訂正はKarteの訂正方針へ接続する対象として扱う．
- Karteを永続記憶の正本とする．最小の能動参加は確定した検索scopeと共有可能な文書・版に対する有限の検索→取得→候補から始める．Runtimeは発話直前にも参加者，期限，revision，抑制，共有制限を確認する．frameworkに人格・記憶・deliveryの正本を移さない．
- 固定workflow，agent core，リアルタイム音声pipeline，TTS engineの採否は別々に扱う．audio.cpp C APIは既存の停止可能なchild worker内に置く実験経路とし，利用者の既存の声を維持する．Pipecatは小さな比較から委譲可能な処理を評価し，turnのownerを二重にしない．

## Consequences

日常の指摘を有限の設定へ反映し，再起動復元と変更単位のundoを提供できる．Runtimeに小さな設定・評価adapterと分離launcherが増える．反面，別daemon，別UI，別記憶DB，独自推論kernel，複数の汎用tool loopを導入せずに済む．自然さや聴感，背景capture，sleep復帰，長時間負荷の実機成績は自動fixtureと区別してRuntimeの結果記録へ残す．既存Reference Architecture PDFは保持する．

## Alternatives considered

Pi固定採用と全体の書直しは選ばない．Pydantic AIは動的検索が必要な場合の候補，Pipecatは音声制御の委譲比較とする．共有GatewayのProfile全reloadは通常版を巻き込むため採らない．feedback原文のsystem promptへの継ぎ足しは型・権限・取消の境界を保てないため採らない．

## Related repositories

`ephy-runtime`：`codex/feat-resident-feedback`のADR-0017，常駐実装，`docs/RESIDENT_FEEDBACK.md`，実験結果が対応する．

## Date

2026-09-14
