const express = require("express");
const router = express.Router();
const Recipe = require("../models/Recipe");

// Get ALL recipes (Only ID, Name, and Image)
router.get("/", async (req, res) => {
  try {
    const recipes = await Recipe.find({}, { _id: 1, "Recipe Name": 1, "Img URL": 1 });
    res.json(recipes);
  } catch (error) {
    console.error("API Error:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

module.exports = router;
