import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.send("111 Hello World!");
});

app.post('/auth/login', (req, res) => {
    console.log(req.body);

    if (req.body)
});

app.listen(4444, (err) => {
  if (err) {
    return console.log(err);
  }

  console.log("Server OK");
});

