const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }, // Store hashed password
  age: { type: Number, required: true },
  gender: { type: String, required: true },
  food: { type: String, required: true }
});

module.exports = mongoose.model("User", UserSchema);
