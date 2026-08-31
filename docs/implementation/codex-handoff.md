# ephy-cam実装用Codexハンドオフ

## 目的

この文書は，[カメラコンテキスト設計](../camera-context.md)を複数リポジトリへ実装する際に，担当Codexへ渡す共通指示とリポジトリ別指示をまとめる．設計上の責任境界を維持し，小さく検証可能なPRへ分割することを目的とする．

## 前提となる決定

- ephy-camは持ち運んで使用する．
- ユーザーが許可した場所と時間の両方を満たす場合だけ，自動撮影を許可する．
- 撮影しただけでは保存・日記掲載を許可しない．写真は別の判断で`accepted`になる．
- Karteの日記は，`accepted`になった写真だけから自動確定できる．
- 撮影許可の詳細設定，実画像，Karte本番データ，認証情報は通常のGitへ保存しない．
- `ephy-physical-ci`はbuild，flash，test，result collectionだけを担当し，production daemonや撮影ポリシーを所有しない．

## 実装順序

以下は依存順であり，期限や所要時間を示すものではない．

1. `ephy-cam`で契約と状態遷移を定義する．
2. `ephy-runtime`で場所・時間ポリシーと短期permit発行を実装する．
3. `ephy-cam`でpermit gate，indicator gate，production transportを実装する．
4. `ephy-runtime`で画像入力，期限付きObservation，能動発話ポリシーを実装する．
5. Karteでaccepted asset importと日記outbox transactionを実装する．
6. `ephy-physical-ci`で契約，hardware stop，artifactを横断検証する．

各段階では，未実装の後続段階をモックまたはsynthetic fixtureで置き換える．実画像やKarte本番データをテストfixtureにしない．

## Codexへの共通指示

次のブロックを各リポジトリ固有の指示の前に付ける．

```text
作業前に，リポジトリ内のAGENTS.md，README，architecture文書，security文書，関連ADR，Git状態，既存PRを確認してください．ユーザーの既存変更を保持し，依頼と無関係な変更を行わないでください．

実装済みの現状と，将来の提案を区別してください．秘密情報，個人情報，実際の撮影画像，実際の位置情報，Karte本番データをGitへ追加しないでください．テストにはsynthetic fixtureだけを使用してください．

責任境界はephy/docs/camera-context.md，ADR-0001，ADR-0002を正としてください．境界を変更する必要が生じた場合は，実装で黙って変更せず，先にephy側へADR変更案を出してください．

変更には対応するテストを追加し，リポジトリ指定のテスト，format，lint，validate_repositoryを実行してください．失敗した検証は，環境要因を含めて隠さず報告してください．

1つのPRでは1つの検証可能な責任だけを扱ってください．merge，release，deploy，実機への本番設定投入は行わないでください．pushとPR作成は，その作業環境で明示承認されている場合だけ行ってください．
```

## `ephy-cam`契約PR

関連Issueは `kirimine170/ephy-cam#1`，親Issueは `kirimine170/ephy#2`．

```text
ephy-camで，既存のXIAO ESP32S3 Sense手動USB captureを壊さずに，portable automatic captureの契約層を実装してください．このPRではproduction transportやschedulerは実装せず，schema，validation，状態遷移，synthetic testsに限定してください．

必須成果物：
- CaptureRequest v1 JSON Schema．
- MediaEnvelope v2 JSON Schema．v1 consumerとの互換方針を文書化すること．
- CapturePermit v1 JSON Schema．
- PhotoAcceptance v1 JSON Schema．
- ephemeral，candidate，accepted，diary-eligible，committed，purgedの有効な状態遷移を検証する小さなドメイン実装．
- deadline，permit expiry，purpose mismatch，capture limit，indicator_required，replayを拒否するsynthetic tests．
- captureだけではacceptedにならないことを固定するtest．

MediaEnvelope v2にはpurpose，retention_class，expires_at，width，height，clock_source，firmware_version，sensor_model，trace_idを追加してください．座標，SSID，caption，人物・感情推論は含めないでください．binary mediaをJSONへ埋め込まないでください．

既存のmanual USB referenceとMediaEnvelope v1のtestを維持してください．PR本文にephy-cam#1とephy#2を関連付け，実装した契約と後続PRへ残した範囲を明記してください．
```

## `ephy-runtime` permit PR

関連Issueは `kirimine170/ephy-runtime#36`，親Issueは `kirimine170/ephy#2`．

```text
ephy-runtimeで，instance localのCapturePolicyを評価し，ephy-cam向けの短期CapturePermitを発行するpolicy componentを実装してください．このPRではカメラ通信，画像推論，Karte書き込みを実装しないでください．

必須要件：
- authorized placeとauthorized local time windowの両方を満たすまでpermitを発行しない．
- policy timezoneから時刻を評価し，permitにはUTCのissued_atとexpires_atを出力する．
- source，allowed purposes，max captures，minimum cooldown，indicator_required，policy revisionを最小権限で含める．
- manual armingまたはauthenticated local assertionをplace evidenceとして扱えるinterfaceを定義する．
- SSID単独，GPS単独，stale evidence，clock uncertainty，revocation，unknown sourceをdenyする．
- full ephy-private configuration，座標履歴，credentialをpermitやlogへ出力しない．
- allow，deny，expiry，revocation，timezone boundary，DST boundaryをsynthetic clockでtestする．

署名方式やtransportはinterfaceの外側へ分離してください．暗号方式を仮実装で固定せず，test用signerとproduction provider interfaceを用意してください．
```

## `ephy-cam` device・gateway PR

関連Issueは `kirimine170/ephy-cam#1`，検証Issueは `kirimine170/ephy-physical-ci#3`．

```text
ephy-camで，CapturePermitとCaptureRequestを受け取るportable device・gateway pathを実装してください．既存のmanual USB captureはdiagnostic pathとして維持してください．

自動撮影は，有効なpermit，許可purpose，deadline，cooldown，capture limit，indicator readyの全条件を満たす場合だけ実行してください．不明な状態はfail closedにしてください．deviceはoutbound connectionだけを開始し，long-lived policyやKarte accessを持たせないでください．

このPRの前に，対象筐体のvisible indicatorとhardware disable方法を設計上確定してください．indicator failure，revocation，network loss，gateway restart，duplicate request，stale permitで撮影しないhardwareまたはintegration testを追加してください．automatic captureのoffline removable-media spoolは実装しないでください．

firmware versionと実際のsensor modelをMediaEnvelopeへ記録し，画像bytesはauthorized stagingへ置いてopaque staging referenceだけを返してください．ログに画像，credential，座標，Wi-Fi identifierを出力しないでください．
```

## `ephy-runtime`画像入力・能動発話PR

関連Issueは `kirimine170/ephy-runtime#35` と `kirimine170/ephy-runtime#36`．

```text
ephy-runtimeで，ephy-camのMediaEnvelope v2を画像入力として受け取り，期限付きObservationとtraceableな能動発話候補を生成するpathを実装してください．Karte canonical writeはこのPRに含めないでください．

必須要件：
- envelope schema，hash，expiry，purposeを検証してからmediaを読む．
- expired mediaまたはunsupported purposeを拒否する．
- Observation v1を定義し，kind，value，confidence，observed_at，expires_at，source_id，capture_id，trace_idを含める．
- emotion，health，personality，identity，intentを画像から断定しない．
- uncertaintyが高い場合は無視または会話で確認する．
- speech cooldown，quiet policy，cancellation，observation expiryを適用する．
- 発話理由をtrace_idから説明できるようにする．
- modelをmockしたsynthetic image fixtureでaccept，reject，expiry，cancel，no-speechをtestする．

モデル固有の出力をそのままmemoryへ保存せず，versioned Observation contractへ正規化してください．
```

## Karte日記PR

関連Issueは `kirimine170/Karte#281`．画像metadataは `#213`，agent境界は `#217`，streaming importは `#245` も確認する．

```text
Karteで，accepted photoだけを取り込むDiaryCandidate v1 outboxと，canonical daily diaryへのatomic promotionを実装してください．ephy-cam deviceやephy-runtimeにcontent treeの直接write権限を与えないでください．

必須要件：
- DiaryCandidate v1のschema validation．
- 各assetについてaccepted decision reference，content hash，media type，size，dimensions，capture time，provenanceを検証する．
- instance IDとlocal dateからidempotency keyを構成し，同じkeyのretryで日記を複製しない．
- image import，metadata，relative Markdown reference，daily entryをtransactionとして扱う．
- 失敗時はoutboxにmachine-readable errorを残し，canonical Markdownとmediaを部分変更しない．
- raw coordinates，Wi-Fi identifier，permit token，hidden visual inferenceを日記へ書かない．
- late acceptance，correction，deletionで同じdaily entryを監査可能に更新する．
- malformed image，hash mismatch，non-accepted asset，duplicate retry，partial failure，path traversalをsynthetic testsで検証する．

日記自動確定は，accepted photoと設定済みfinalization policyがある場合だけ許可してください．写真acceptance自体をこのPRで自動化しないでください．
```

## `ephy-physical-ci`検証PR

関連Issueは `kirimine170/ephy-physical-ci#3`．

```text
ephy-physical-ciで，ephy-camとephy-runtimeが提供するcommandを呼び出し，portable automatic captureのcontractとhardware stop条件を検証してください．device firmware，camera pins，sensor profiles，production scheduler，production media storageをphysical-ciへ移さないでください．

必須成果物：
- pinned toolchainとboard profileを使うbuild・flash job．
- device identity，firmware version，sensor model，indicator readinessを記録するresult schema．
- valid permitで1枚だけ撮影できるtest．
- expired permit，revoked permit，purpose mismatch，duplicate request，indicator failureで撮影しないtest．
- JPEG decode，dimensions，size，SHA-256，MediaEnvelope v2 validation．
- artifactとlogのretentionをboundedにし，検証後にmaster imageを通常Gitへ残さないcleanup．

実機がない環境ではhardware testをskipとして明示し，schemaとhost-side testsは実行してください．skipをpassへ偽装しないでください．
```

## PR完了報告フォーマット

担当Codexには，最終報告を次の順で返させる．

```text
結果：実装した責任を1文で記述．

変更：主要ファイルとcontract versionを列挙．

検証：実行したtest，lint，validator，hardware testと結果を列挙．skipまたは環境失敗を分離．

境界：このPRで意図的に実装しなかった後続範囲を列挙．

レビュー事項：安全性，互換性，未決定事項のうち，人間の判断が必要な点だけを列挙．

Issue・PR：関連Issueと作成したPRのURL．
```

## 人間が先に決める項目

次の項目はCodexに推測させず，実装前にユーザーが選択する．

- 対象筐体で独立確認できるvisible capture indicatorとhardware disable機構．
- 同席者を検出した場合に常に停止するか，許可場所ごとに設定できるか．
- 最初のproduction gatewayを動かすhostと，portable deviceのnetwork provisioning方法．
- `candidate`を`accepted`へ変えるユーザー操作．
- 日記を確定する日境界と，遅れて採用された写真を追記する際の表示・通知方法．

