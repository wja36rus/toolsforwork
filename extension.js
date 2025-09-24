const vscode = require("vscode");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

function activate(context) {
  console.log("Enum Updater extension is now active!");

  vscode.commands.getCommands().then((commands) => {
    if (commands.includes("toolsforwork.update-enum")) {
      console.log("✅ Command toolsforwork.update-enum is registered");
    } else {
      console.log("❌ Command toolsforwork.update-enum is NOT registered");
    }
  });

  let disposable = vscode.commands.registerCommand(
    "toolsforwork.update-enum",
    async function () {
      // Получаем активный текстовый редактор
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showErrorMessage("Нет активного редактора!");
        return;
      }

      // Получаем путь к текущему файлу
      const currentFile = editor.document.fileName;

      // Проверяем, что файл TypeScript
      if (!currentFile.endsWith(".ts") && !currentFile.endsWith(".tsx")) {
        vscode.window.showWarningMessage(
          "Расширение работает только с TypeScript файлами (.ts, .tsx)"
        );
        return;
      }

      // Получаем путь к Python скрипту
      const extensionPath = context.extensionPath;
      const pythonScriptPath = path.join(
        extensionPath,
        "python",
        "enum_updater.py"
      );

      // Проверяем существование Python скрипта
      if (!fs.existsSync(pythonScriptPath)) {
        vscode.window.showErrorMessage(
          `Python скрипт не найден: ${pythonScriptPath}`
        );
        return;
      }

      // Показываем индикатор выполнения
      vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Обновление enum...",
          cancellable: false,
        },
        async (progress) => {
          return new Promise((resolve) => {
            // Запускаем Python скрипт с указанием кодировки UTF-8
            const pythonProcess = spawn(
              "python",
              ["-X", "utf8", pythonScriptPath, currentFile],
              {
                env: { ...process.env, PYTHONIOENCODING: "utf-8" },
              }
            );

            let output = "";
            let errorOutput = "";

            pythonProcess.stdout.on("data", (data) => {
              output += data.toString();
            });

            pythonProcess.stderr.on("data", (data) => {
              errorOutput += data.toString();
            });

            pythonProcess.on("close", (code) => {
              if (code === 0) {
                // Успешное выполнение
                vscode.window.showInformationMessage(
                  "Enum успешно преобразован!"
                );

                // Показываем детальный вывод
                if (output) {
                  const outputChannel =
                    vscode.window.createOutputChannel("Enum Updater");
                  outputChannel.clear();
                  outputChannel.appendLine("Результат преобразования:");
                  outputChannel.appendLine(output);
                  outputChannel.show();
                }

                // Перезагружаем файл в редакторе
                vscode.commands.executeCommand("workbench.action.files.revert");
              } else {
                // Ошибка выполнения
                const errorMessage =
                  errorOutput || output || "Неизвестная ошибка";
                vscode.window.showErrorMessage(
                  `Ошибка при преобразовании enum: ${errorMessage}`
                );

                if (errorOutput || output) {
                  const errorChannel = vscode.window.createOutputChannel(
                    "Enum Updater Errors"
                  );
                  errorChannel.clear();
                  errorChannel.appendLine("Ошибки:");
                  if (errorOutput) errorChannel.appendLine(errorOutput);
                  if (output) errorChannel.appendLine(output);
                  errorChannel.show();
                }
              }
              resolve();
            });

            pythonProcess.on("error", (error) => {
              vscode.window.showErrorMessage(
                `Не удалось запустить Python: ${error.message}`
              );
              if (error.code === "ENOENT") {
                vscode.window.showErrorMessage(
                  "Python не установлен или не добавлен в PATH"
                );
              }
              resolve();
            });
          });
        }
      );
    }
  );

  let importUpdater = vscode.commands.registerCommand(
    "toolsforwork.update-import",
    async function () {
      // Получаем активный текстовый редактор
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showErrorMessage("Нет активного редактора!");
        return;
      }

      // Получаем путь к текущему файлу
      const currentFile = editor.document.fileName;

      // Проверяем, что файл TypeScript
      if (!currentFile.endsWith(".ts") && !currentFile.endsWith(".tsx")) {
        vscode.window.showWarningMessage(
          "Расширение работает только с TypeScript файлами (.ts, .tsx)"
        );
        return;
      }

      // Получаем путь к Python скрипту
      const extensionPath = context.extensionPath;
      const pythonScriptPath = path.join(
        extensionPath,
        "python",
        "import_updater.py"
      );

      // Проверяем существование Python скрипта
      if (!fs.existsSync(pythonScriptPath)) {
        vscode.window.showErrorMessage(
          `Python скрипт не найден: ${pythonScriptPath}`
        );
        return;
      }

      // Показываем индикатор выполнения
      vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Обновление импортов...",
          cancellable: false,
        },
        async (progress) => {
          return new Promise((resolve) => {
            // Запускаем Python скрипт с указанием кодировки UTF-8
            const pythonProcess = spawn(
              "python",
              ["-X", "utf8", pythonScriptPath, currentFile],
              {
                env: { ...process.env, PYTHONIOENCODING: "utf-8" },
              }
            );

            let output = "";
            let errorOutput = "";

            pythonProcess.stdout.on("data", (data) => {
              output += data.toString();
            });

            pythonProcess.stderr.on("data", (data) => {
              errorOutput += data.toString();
            });

            pythonProcess.on("close", (code) => {
              if (code === 0) {
                // Успешное выполнение
                vscode.window.showInformationMessage(
                  "Импорты успешно преобразованы!"
                );

                // Показываем детальный вывод
                if (output) {
                  const outputChannel =
                    vscode.window.createOutputChannel("Import Updater");
                  outputChannel.clear();
                  outputChannel.appendLine("Результат преобразования:");
                  outputChannel.appendLine(output);
                  outputChannel.show();
                }

                // Перезагружаем файл в редакторе
                vscode.commands.executeCommand("workbench.action.files.revert");
              } else {
                // Ошибка выполнения
                const errorMessage =
                  errorOutput || output || "Неизвестная ошибка";
                vscode.window.showErrorMessage(
                  `Ошибка при преобразовании импортов: ${errorMessage}`
                );

                if (errorOutput || output) {
                  const errorChannel = vscode.window.createOutputChannel(
                    "Import Updater Errors"
                  );
                  errorChannel.clear();
                  errorChannel.appendLine("Ошибки:");
                  if (errorOutput) errorChannel.appendLine(errorOutput);
                  if (output) errorChannel.appendLine(output);
                  errorChannel.show();
                }
              }
              resolve();
            });

            pythonProcess.on("error", (error) => {
              vscode.window.showErrorMessage(
                `Не удалось запустить Python: ${error.message}`
              );
              if (error.code === "ENOENT") {
                vscode.window.showErrorMessage(
                  "Python не установлен или не добавлен в PATH"
                );
              }
              resolve();
            });
          });
        }
      );
    }
  );

  context.subscriptions.push(disposable, importUpdater);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
