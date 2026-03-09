const mongoose = require("mongoose");

const recipeSchema = new mongoose.Schema({
  _id: mongoose.Schema.Types.ObjectId,
  "Recipe Name": { type: String, unique: true },
  "Cusine": { type: String },
  "Dish Type": { type: String },
  "INGREDIENTS": { type: String },
  "Preparation Steps": { type: String },
  "Cooking Steps": { type: String },
  "Img URL": { type: String }
}, { collection: "Full_Recipe" });

module.exports = mongoose.model("Recipe", recipeSchema);
