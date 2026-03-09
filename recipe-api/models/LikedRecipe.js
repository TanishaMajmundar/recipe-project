const mongoose = require("mongoose");

const LikedRecipeSchema = new mongoose.Schema({
    userId: { type: String, required: true },
    recipeId: { type: mongoose.Schema.Types.ObjectId, ref: "Full_Recipe", required: true }
});

module.exports = mongoose.model("Liked_Recipe", LikedRecipeSchema);