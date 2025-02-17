// отправить запрос на бекенд
function triggerPythonScript() {

    var url = "https://dollarsnow.org/sync_calendar";
    try {
        var response = UrlFetchApp.fetch(url, {
            "method": "post",
            "muteHttpExceptions": true
        });

        var jsonResponse = JSON.parse(response.getContentText());

        if (jsonResponse.status === "success") {
            SpreadsheetApp.getUi().alert("✅ Success\n" + jsonResponse.message);
        } else {
            SpreadsheetApp.getUi().alert("❌ Error\n" + jsonResponse.message);
        }

    } catch (error) {
        SpreadsheetApp.getUi().alert("🚨 Request failed\n" + error.message);
    }
}


// добавить меню над таблицей
function onOpen() {
    var ui = SpreadsheetApp.getUi();

    ui.createMenu("Внести в календарь")
        .addItem("Внести в календарь", "triggerPythonScript")
        .addToUi();
}
