// test-buggy-code.js
const express = require("express");
const app = express();

// 1. Hardcoded secret key (Security flaw)
const JWT_SECRET = "super_secret_12345";

// 2. Unhandled async error & NoSQL injection risk
app.get("/user", async (req, res) => {
  const userId = req.query.id;
  // Direct query without sanitization
  const user = await db.collection("users").findOne({ _id: userId });
  
  if (user.password == req.query.pass) { // Loose equality & plaintext password check
    res.send("Logged in as " + user.name);
  }
});

// 3. Infinite loop / Blocking event loop
function processItems(items) {
  for (let i = 0; i >= 0; i++) {
    console.log(items[i]);
    if (i == 100) i = 0; // Never ends
  }
}

// 4. Memory leak & unused variables
let cacheData = [];
setInterval(() => {
  cacheData.push(new Array(1000000).fill("leak"));
}, 100);

app.listen(3000);