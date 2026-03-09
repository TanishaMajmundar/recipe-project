const express = require("express");
const router = express.Router();
const LikedRecipe = require("../models/LikedRecipe");
const Recipe = require("../models/Recipe"); // This is your existing recipes model
const mongoose = require("mongoose");

// ✅ Like a recipe
router.post("/", async (req, res) => {
    try {
        const { userId, recipeId } = req.body;

        if (!mongoose.Types.ObjectId.isValid(recipeId)) {
            return res.status(400).json({ error: "Invalid recipe ID" });
        }

        const recipe = await Recipe.findById(recipeId);
        if (!recipe) return res.status(404).json({ error: "Recipe not found" });

        const alreadyLiked = await LikedRecipe.findOne({ userId, recipeId });
        if (alreadyLiked) return res.status(400).json({ error: "Recipe already liked" });

        const likedRecipe = new LikedRecipe({ userId, recipeId });
        await likedRecipe.save();

        res.json({ message: "Recipe liked successfully" });
    } catch (error) {
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// ✅ Get liked recipes for a user
router.get("/:userId", async (req, res) => {
    try {
        const likedRecipes = await LikedRecipe.find({ userId: req.params.userId })
            .populate("recipeId");
        res.json(likedRecipes);
    } catch (error) {
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// ✅ Unlike a recipe
router.delete("/:userId/:recipeId", async (req, res) => {
    try {
        await LikedRecipe.findOneAndDelete({ userId: req.params.userId, recipeId: req.params.recipeId });
        res.json({ message: "Recipe unliked successfully" });
    } catch (error) {
        res.status(500).json({ error: "Internal Server Error" });
    }
});

module.exports = router;