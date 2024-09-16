function onEdit(e) {
  try {
    var sheet = e.source.getActiveSheet();
    var range = e.range;
    var rowNum = range.getRow();
    var lastColumn = sheet.getLastColumn();
    var columnNames = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];

    Logger.log("Active sheet: " + sheet.getName());
    Logger.log("Row number: " + rowNum);
    Logger.log("Column names: " + columnNames);

    var dbUrl = 'jdbc:mysql://<DB:HOST>:<DB:PORT>/<DB:NAME>';
    var user = <DB:USER>;
    var password = <DB:PASSWORD>;

    var conn = Jdbc.getConnection(dbUrl, user, password);
    Logger.log("Database connection established.");

    var stmt = conn.prepareStatement("UPDATE global_variables SET value = 0 WHERE variable_name = 'sheets';");
    stmt.executeUpdate();
    Logger.log("Updated 'sheets' value to 0.");
    stmt.close();

    var tableName = "`" + sheet.getParent().getName().replace(/ /g, "_") + "_" + sheet.getSheetName().replace(/ /g, "_") + "`";
    Logger.log("Table name: " + tableName);

    if (rowNum === 1) {
      var currentColumnsQuery = `SHOW COLUMNS FROM ${tableName};`;
      Logger.log("Fetching existing columns with query: " + currentColumnsQuery);

      var stmt = conn.createStatement();
      var results = stmt.executeQuery(currentColumnsQuery);
      var existingColumns = [];
      while (results.next()) {
        existingColumns.push(results.getString("Field")); 
      }
      Logger.log("Existing columns in table: " + existingColumns);

      if (existingColumns[0] !== 'ROW_ID') {
        throw new Error("First column must be 'ROW_ID'. Aborting alter operation.");
      }

      var alterQueries = [];
      for (var i = 0; i < columnNames.length; i++) { 
        var newColumnName = columnNames[i] ? columnNames[i] : "Col" + String.fromCharCode(65 + i); 
        columnNames[i] = newColumnName;
        if (existingColumns[i+1]) {
          var alterQuery = `ALTER TABLE ${tableName} CHANGE COLUMN \`${existingColumns[i+1]}\` \`${newColumnName}\` VARCHAR(255);`;
        } else {
          var alterQuery = `ALTER TABLE ${tableName} ADD COLUMN \`${newColumnName}\` VARCHAR(255);`;
        }
        Logger.log("Generated alter query: " + alterQuery);
        alterQueries.push(alterQuery);
      }

      for (var j = 0; j < alterQueries.length; j++) {
        var alterStmt = conn.prepareStatement(alterQueries[j]);
        alterStmt.executeUpdate();
        Logger.log("Executed query: " + alterQueries[j]);
        alterStmt.close();
      }

      Logger.log("Column names updated successfully.");
      
      var stmt = conn.prepareStatement("UPDATE global_variables SET value = 1 WHERE variable_name = 'sheets';");
      stmt.executeUpdate();
      Logger.log("Updated 'sheets' value to 1.");
      stmt.close();

      conn.close();
      Logger.log("Database connection closed.");
      return; 
    }

    var rowData = sheet.getRange(rowNum, 1, 1, lastColumn).getValues()[0];
    
    Logger.log("Row data: " + rowData);

    var primaryKeyValue = rowNum-1;

    for (var i = 0; i < columnNames.length; i++) {
      if (!columnNames[i]) {
        columnNames[i] = "Col" + String.fromCharCode(65 + i);  // Assign default column names
      }
    }
    
    Logger.log("Updated column names: " + columnNames);

    var insertColumns = columnNames.map(col => "`" + col + "`").join(", ");
    var placeholders = columnNames.map(() => "?").join(", ");
    var updateClause = columnNames.map(col => "`" + col + "` = VALUES(`" + col + "`)").join(", ");

    var query = `
      INSERT INTO ${tableName} (\`ROW_ID\`, ${insertColumns}) 
      VALUES (?, ${placeholders}) 
      ON DUPLICATE KEY UPDATE ${updateClause}
    `;

    Logger.log("SQL Query: " + query);

    var stmt = conn.prepareStatement(query);
    stmt.setInt(1, primaryKeyValue);

    for (var i = 0; i < rowData.length; i++) {
      var value = rowData[i] ? rowData[i].toString() : null;
      Logger.log("Inserting value for column " + columnNames[i] + ": " + value);
      stmt.setString(i + 2, value);
    }

    Logger.log("Executing SQL query...");
    stmt.executeUpdate();
    Logger.log("SQL query executed successfully.");

    stmt.close();

    stmt = conn.prepareStatement("UPDATE global_variables SET value = 1 WHERE variable_name = 'sheets';");
    stmt.executeUpdate();
    Logger.log("Updated 'sheets' value to 1.");
    stmt.close();

    conn.close();
    Logger.log("Database connection closed.");
  } catch (error) {
    Logger.log("Error: " + error.message);
  }
}


function testOnEdit() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(4, 1).setValue("Test 2");
  var event = {
    source: SpreadsheetApp.getActiveSpreadsheet(),
    range: sheet.getRange(4, 1), 
    value: "Test 3", 
  };
  
  onEdit(event);
}

