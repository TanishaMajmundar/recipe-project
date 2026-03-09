const express = require("express");
const router = express.Router();
const Recipe = require("../models/Recipe");

// Get recipes filtered by name or dish type
router.get("/", async (req, res) => {
  try {
    let filter = {};  // Empty filter object

    // If 'name' query exists, filter by recipe name (case insensitive)
    if (req.query.name) {
      filter["Recipe Name"] = new RegExp(req.query.name, "i");
    }

    // If 'dishType' query exists, filter by dish type
    if (req.query.dishType) {
      filter["Dish Type"] = req.query.dishType;  // Match exact dish type
    }

    // Fetch filtered recipes from database
    const recipes = await Recipe.find(filter, { _id: 1, "Recipe Name": 1, "Img URL": 1 });

    res.json(recipes);
  } catch (error) {
    console.error("❌ API Error:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

module.exports = router;