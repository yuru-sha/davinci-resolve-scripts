# DaVinci Resolve Scripts

DaVinci Resolve用のPythonスクリプト集。画像処理とプロジェクト設定管理のためのツールを提供します。

## 特徴

### EXIFフレームスクリプト

- **2つのバージョン**: DaVinci Resolve FreeとStudioの両方に対応
  - **Studio版**: カスタマイズ可能なUI（枠色、サイズ、テキストオーバーライド）
  - **Free版**: 固定レイアウト（白枠Polaroidスタイル）
- **幅広いフォーマット対応**: JPEG、PNG、RAW（ARW/CR2/CR3/NEF/DNG/RAF/ORF）
- **自動EXIF抽出**: カメラ名、レンズ、撮影設定（焦点距離、絞り、シャッター速度、ISO）
- **動的パス検出**: 環境に応じてPython依存関係を自動検出

### プロジェクト設定コピースクリプト

- **2つのバージョン**: DaVinci Resolve FreeとStudioの両方に対応
  - **Studio版**: Fusionダイアログで対話的に操作
  - **Free版**: コンソール入力による対話型CLI
- **簡単な設定コピー**: 既存プロジェクトの全設定を新規プロジェクトにコピー
- **デフォルト名自動生成**: 「ソース名 Copy」形式で提案（編集可能）
- **詳細レポート**: 適用成功/失敗の詳細を表示

### 共通機能

- **クロスプラットフォーム対応**: macOSとWindows両方で動作

## 必要要件

- **DaVinci Resolve** (Free または Studio)
- **Python 3.11+** （システムにインストール済みであること）
  - ⚠️ **重要**: DaVinci ResolveがPython3を認識できない場合、スクリプトはメニューに表示されません
  - Free版: Python3が未インストールの場合、ダウンロードURLが表示されます
  - Studio版: システムのPython 3.9-3.11を推奨
- **uv** (Pythonパッケージマネージャー)

## インストール

### 1. 依存関係のインストール

```bash
# リポジトリをクローン
git clone https://github.com/yuru-sha/davinci-resolve-scripts.git
cd davinci-resolve-scripts

# Python依存関係をインストール
uv sync
```

### 2. 環境チェック

```bash
# Python、ライブラリ、インストール先を確認
make check
```

**Windowsの場合**:
```bash
python scripts/install.py check
```

### 3. スクリプトのインストール

```bash
# 対話式インストール（Free版またはStudio版を選択）
# Free版: EXIF Frame (Lite) + Copy Project Settings (Lite)
# Studio版: EXIF Frame + Copy Project Settings
make install
```

**Windowsの場合**:
```bash
python scripts/install.py install
```

スクリプトは以下にインストールされます:

**macOS**:
```
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility
```

**Windows**:
```
%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility
```

### 4. DaVinci Resolveの再起動

スクリプトが表示されない場合は、DaVinci Resolveを再起動してください。

## 使い方

### EXIFフレームスクリプト

1. DaVinci Resolveでプロジェクトを開く
2. タイムラインで処理したいクリップの上に再生ヘッドを配置
3. メニューから **Workspace > Scripts > Utility** を選択
4. `add_exif_frame_dv.py` (Studio) または `add_exif_frame_dv_lite.py` (Free) を実行

#### Studio版の機能

- **枠の色**: 白または黒を選択
- **枠のサイズ**: 0-20%でスライダー調整
- **テキストオーバーライド**: カメラ名や撮影設定を手動編集可能
- **Polaroidスタイル**: 下部の枠を大きくするオプション

#### Free版の仕様

- 固定の白枠Polaroidレイアウト
- UI設定なし（シンプル設計）
- Fusion APIの制限を回避

### プロジェクト設定コピースクリプト

1. DaVinci Resolveを起動
2. データベースを開く
3. メニューから **Workspace > Scripts > Utility** を選択
4. `copy_project_settings_dv.py` (Studio) または `copy_project_settings_dv_lite.py` (Free) を実行

#### Studio版の使い方

1. ダイアログでソースプロジェクトを選択
2. 新規プロジェクト名を入力（デフォルト: 「ソース名 Copy」）
3. 自動的に設定がコピーされた新規プロジェクトが作成される
4. 結果ダイアログで適用結果を確認

#### Free版の使い方

1. コンソールで番号を入力してプロジェクトを選択
2. 新規プロジェクト名を入力（Enterでデフォルト値使用）
3. 設定適用結果がコンソールに表示される

#### 注意事項

- スクリプト実行時にソースプロジェクトがロードされるため、現在開いているプロジェクトは閉じられます
- 一部の読み取り専用設定は適用できません（自動的にスキップされ、失敗リストに表示されます）
- 同名プロジェクトが既に存在する場合、エラーメッセージが表示されます

## 出力

### EXIFフレームスクリプト

- 元の画像と同じディレクトリに `_framed.jpg` という接尾辞付きで保存
- すでに `_framed` が付いているファイルはスキップ
- タイムライン上のクリップは自動的に置き換え（Studio版のみ）

### プロジェクト設定コピースクリプト

- **プロジェクト**: ソースプロジェクトと同じフォルダに新規プロジェクトが作成されます
- **設定**: 全ての設定（解像度、フレームレート、色空間など）が新規プロジェクトに適用されます
- **レポート**: Studio版はダイアログ、Free版はコンソールで適用結果を表示

## 開発

### Lintとフォーマット

```bash
# Linterを実行
make lint

# フォーマッターを実行
make format

# 自動修正（lint + format）
make fix
```

### アンインストール

```bash
# macOS/Linux
make uninstall

# Windows
python scripts/install.py uninstall
```

## 技術詳細

### アーキテクチャ

1. **EXIF抽出**: Pillow（標準画像）とrawpy/exifread（RAWファイル）の二重パス
2. **画像処理**: 動的な枠計算とPolaroidスタイルレイアウト
3. **テキストレンダリング**: カメラ情報と撮影設定の自動フォーマット
4. **DaVinci Resolve統合**: タイムライン上のクリップを処理

### パス検出

スクリプトは以下の優先順位でPython依存関係を検出します：

1. 環境変数 `DAVINCI_RESOLVE_SCRIPTS_VENV`
2. インストール時に埋め込まれたパス

手動でパスを指定する場合：

**macOS/Linux**:
```bash
export DAVINCI_RESOLVE_SCRIPTS_VENV=/path/to/.venv/lib/python3.11/site-packages
```

**Windows (PowerShell)**:
```powershell
$env:DAVINCI_RESOLVE_SCRIPTS_VENV="C:\path\to\.venv\Lib\site-packages"
```

**Windows (コマンドプロンプト)**:
```cmd
set DAVINCI_RESOLVE_SCRIPTS_VENV=C:\path\to\.venv\Lib\site-packages
```

### システム要件の詳細

- **Python**: 3.11以上（DaVinci Resolve Studio 19/20との互換性）
- **ライブラリ**: Pillow、rawpy、exifread
- **プラットフォーム**: macOS、Windows（自動検出）

### クロスプラットフォーム対応

Pythonベースのインストーラー（[scripts/install.py](scripts/install.py)）により、以下を自動処理：

- プラットフォーム自動検出（macOS / Windows）
- OS別インストールパス選択
- 仮想環境のsite-packagesパス検出
- スクリプトへのパス埋め込み

## トラブルシューティング

### ライブラリが見つからない

```
ERROR: Could not find required libraries.
```

**解決策**:
1. `uv sync` を実行して依存関係をインストール
2. `make check` (またはWindows: `python scripts/install.py check`) で環境を確認
3. 必要に応じて環境変数を設定

### スクリプトがメニューに表示されない

**解決策**:
1. DaVinci Resolveを完全に再起動
2. インストール先ディレクトリを確認
   - macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`
   - Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility`
3. `make install` (またはWindows: `python scripts/install.py install`) を再実行

### Windows環境でMakefileが使えない

**解決策**:

Pythonスクリプトを直接使用してください：

```bash
# 環境チェック
python scripts/install.py check

# インストール
python scripts/install.py install

# アンインストール
python scripts/install.py uninstall
```

## ライセンス

このプロジェクトのライセンスについては、LICENSEファイルを参照してください。

## 貢献

Issue報告やPull Requestを歓迎します！

## 作者

yuru-sha
