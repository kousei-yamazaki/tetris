@echo off
chcp 65001 > nul
cls

echo ====================================================
echo 【警告】Gitのコミット履歴を完全にリセットします。
echo この操作を行うと、過去の履歴はすべて削除され、
echo リモートリポジトリ（origin main）も強制上書きされます。
echo ====================================================
set /p choice="本当にGitの履歴をリセットしてよろしいですか？ [y/N]: "

if /i "%choice%" equ "y" goto start_process
goto cancel_process

:start_process
echo.
echo 処理を開始します...
echo ----------------------------------------------------

echo [1/6] 新しい一時ブランチを作成中...
git checkout --orphan latest_branch
if %errorlevel% neq 0 goto error

echo.
echo [2/6] ファイルをステージング中...
git add -A
if %errorlevel% neq 0 goto error

echo.
echo [3/6] コミットを作成中...
git commit -m "Reset history to clean up repository"
if %errorlevel% neq 0 goto error

echo.
echo [4/6] 古い main ブランチを削除中...
git branch -D main
if %errorlevel% neq 0 goto error

echo.
echo [5/6] ブランチ名を main に変更中...
git branch -m main
if %errorlevel% neq 0 goto error

echo.
echo [6/6] リモートに強制プッシュ中...
git push -f origin main
if %errorlevel% neq 0 goto error

echo.
echo ----------------------------------------------------
echo 【成功】すべての処理が正常に完了しました！
echo.
pause
exit /b

:cancel_process
echo.
echo ----------------------------------------------------
echo 処理はキャンセルされました。履歴は変更されていません。
echo.
pause
exit /b

:error
echo.
echo ----------------------------------------------------
echo 【エラー】コマンドの実行中にエラーが発生しました。
echo 処理を中断します。
echo.
pause
exit /b