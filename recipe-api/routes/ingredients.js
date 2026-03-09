const express = require("express");
const router = express.Router();
const Recipe = require("../models/Recipe"); // Import Recipe model

// Get all unique ingredients
router.get("/", async (req, res) => {
    try {
        const recipes = await Recipe.find({}, { "INGREDIENTS": 1, _id: 0 });

        let ingredientSet = new Set();

        recipes.forEach(recipe => {
            let ingredients = recipe.INGREDIENTS.split(",").map(ing => ing.trim().toLowerCase());
            ingredients.forEach(ing => ingredientSet.add(ing));
        });

        // Remove common ingredients
        const ignore = [];

        const uniqueIngredients = [...ingredientSet].filter(ing => !ignore.includes(ing));

        res.json({ ingredients: uniqueIngredients });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Failed to fetch ingredients" });
    }
});

module.exports = router;
