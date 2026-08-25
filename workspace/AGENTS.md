# Ephy統合ワークスペース規則

このファイルは，Git管理しないworkspaceルートの`AGENTS.md`の正本です．workspaceをbootstrapした後，ルートへコピーして使用します．

- workspaceルート自体をGit repositoryにしない．
- 各repositoryはworkspace直下へ横並びに配置し，個別のGit履歴とremoteを維持する．
- Git submodule，subtree，monorepo化を行わない．
- 作業前に対象repoごとの`AGENTS.md`，Git状態，remote URLを確認する．
- dirtyなrepoをpull，checkout，reset，cleanしない．
- repo間関係は各repoの`.ephy/project.yaml`へ記載し，中央manifestへ重複記載しない．
- `ephy-private`と`karte-docs`は通常の一括clone対象に含めない．
- `ephy-private`をworker，physical CI，camera端末へ配布しない．
- raw conversation，日常memory，個人情報，credential，秘密鍵，raw LoRA dataset，model weight，camera master画像をGitへ追加しない．
- merge，release，deploy，default branchのforce pushを行わない．
- 実装変更には対応するtestを追加し，repo固有の検証を完了してからpushする．
- 日本語文書の句読点は「，」「．」を使用する．
- 実装済みの状態と提案を区別し，根拠のない期限や進捗率を作らない．
