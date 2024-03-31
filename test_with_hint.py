sqlinjection_source = '''
const app = require("express")(),
      pg = require("pg"),
      pool = new pg.Pool(config);

app.get("search", function handler(req, res) {
  // BAD: the category might have SQL special characters in it
  var query1 =
    "SELECT ITEM,PRICE FROM PRODUCT WHERE ITEM_CATEGORY='" +
    req.params.category +
    "' ORDER BY PRICE";
  pool.query(query1, [], function(err, results) { //Building a database query from user-controlled sources is vulnerable to insertion of malicious code by the user.
    // process results
  });
});

'''




nosqlinjection_source = '''
const express = require("express");
const mongoose = require("mongoose");
const Todo = mongoose.model(
  "Todo",
  new mongoose.Schema({ text: { type: String } }, { timestamps: true })
);

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.delete("/api/delete", async (req, res) => {
  let id = req.body.id;

  await Todo.deleteOne({ _id: id }); // bug: Building a database query from user-controlled sources is vulnerable to insertion of malicious code by the user.

  res.json({ status: "ok" });
});

'''



