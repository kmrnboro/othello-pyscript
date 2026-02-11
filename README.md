# Othello Pyscript

PythonとPyScriptを使用して構築されたWebベースのオセロ（リバーシ）ゲームです。サーバーサイドのロジックなしで、完全にブラウザ上で動作します。

## 機能
- **対戦モード**:
    - PvP（プレイヤー対プレイヤー）
    - プレイヤー対ランダムAI (Easy)
    - プレイヤー対Greedy AI (Medium)
    - プレイヤー対Minimax AI (Hard)
- **アシスト機能**:
    - 有効手の表示（黒/白 個別のスイッチ）
    - 最善手の表示（黒/白 個別のスイッチ、金色ハイライト）
- **カスタマイズ**:
    - プレイヤーの手番選択（先手・黒 / 後手・白）
    - 完全日本語化UI
- **レスポンシブデザイン**: モバイル（iPhone/iPad）およびデスクトップでプレイ可能

## 開発環境のセットアップ

このプロジェクトでは依存関係の管理に `uv` を使用しています。

1. **uvのインストール**:
   ```bash
   pip install uv
   ```

2. **依存関係のインストール**:
   ```bash
   uv sync
   ```

3. **テストの実行**:
   ```bash
   uv run pytest tests/
   ```

4. **ローカルサーバーの起動**:
   PyScriptのCORS問題を回避するため、ローカルでプレイするにはWebサーバーを起動する必要があります。
   ```bash
   python -m http.server 8000
   ```
   その後、ブラウザで [http://localhost:8000](http://localhost:8000) を開いてください。

### 開発時の注意点
`main.py` などで `import pyscript` や `import js` していますが、これらはブラウザ（PyScriptランタイム）内で提供されるモジュールであり、標準のPyPIパッケージではありません。
そのため、ローカル開発環境（VS Codeなど）では `mock_imports` ディレクトリ内のダミーモジュールを参照するように設定し、インポートエラー（赤波線）を回避しています。`uv add` でこれらを追加する必要はありません（しても動きません）。

## GUIテストの自動化について（提案）

ブラウザ上での動作（クリックして石が返るか、AIが応答するかなど）を自動テストするには、**Playwright** の導入を推奨します。

### Playwrightによるテスト例

1. **インストール**:
   ```bash
   uv add --dev pytest-playwright
   uv run playwright install
   ```

2. **テストコード例 (`tests/test_gui.py`)**:
   ```python
   from playwright.sync_api import Page, expect

   def test_othello_gameplay(page: Page):
       # ローカルサーバーが起動している前提
       page.goto("http://localhost:8000")
       
       # タイトル確認
       expect(page).to_have_title("Othello Pyscript")
       
       # 黒の初手 (2, 3) をクリック
       # dataset-row="2", dataset-col="3" の要素を探す
       cell = page.locator(".cell[data-row='2'][data-col='3']")
       cell.click()
       
       # 石が置かれたか確認（classにblackが含まれるか）
       expect(cell).to_have_class(re.compile(r"black"))
       
       # ターンが白に変わったか確認
       status = page.locator("#status")
       expect(status).to_contain_text("Turn: White")
   ```

このように、Pythonコードでブラウザ操作を自動化し、E2E（End-to-End）テストを行うことが可能です。
