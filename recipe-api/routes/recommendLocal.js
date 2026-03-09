const express = require("express");
const router = express.Router();
const { spawn } = require("child_process");
const Recipe = require("../models/Recipe");

router.post("/", async (req, res) => {

    const { ingredients } = req.body;

    if (!ingredients || ingredients.length === 0) {
        return res.status(400).json({ error: "No ingredients provided" });
    }

    const ingredientString = ingredients.join(",");

    const pythonProcess = spawn("python", [
        "python/ai_recipe_model.py",
        ingredientString
    ]);

    let result = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
        result += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
    });

    pythonProcess.on("close", async () => {

        if (errorOutput) {
            console.error("Python Error:", errorOutput);
        }

        try {

            const pythonResults = JSON.parse(result);

            // Get recipe IDs
            const ids = pythonResults.map(r => r._id);

            // Fetch recipes from MongoDB
            const recipes = await Recipe.find({ _id: { $in: ids } });

            // Merge recommendation info with recipe data
            const merged = pythonResults.map(rec => {

                const recipe = recipes.find(
                    r => r._id.toString() === rec._id
                );

                if (!recipe) return null;

                return {
                    ...recipe.toObject(),
                    match_count: rec.match_count,
                    total_ingredients: rec.total_ingredients,
                    matched_ingredients: rec.matched_ingredients,
                    missing_ingredients: rec.missing_ingredients
                };

            }).filter(Boolean);

            res.json({ recipes: merged });

        } catch (error) {
            console.error("Parse Error:", error);
            res.status(500).json({ error: "Failed to parse Python output" });
        }

    });

});

module.exports = router;