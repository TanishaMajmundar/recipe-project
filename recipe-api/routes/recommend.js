const express = require("express");
const router = express.Router();
const axios = require("axios");

const HUGGINGFACE_API_TOKEN = process.env.HUGGINGFACE_API_TOKEN;

router.post("/", async (req, res) => {
  try {
    const { ingredients } = req.body;

    if (!ingredients || ingredients.length === 0) {
      return res.status(400).json({ error: "No ingredients provided" });
    }

    const prompt = `
I have these ingredients: ${ingredients.join(", ")}.
Suggest 3 Indian recipes I can make. For each, include:
- Recipe Name
- Cuisine
- Dish Type
- Preparation Time and Cooking Time
- Ingredients
- 3 to 5 Cooking Steps
- A short description
Format the output as a JSON array.
`;

    const hfResponse = await axios.post(
      "https://api-inference.huggingface.co/pipeline/text-generation/mistralai/Mistral-7B-Instruct-v0.1",
      {
        inputs: prompt,
      },
      {
        headers: {
          Authorization: `Bearer ${HUGGINGFACE_API_TOKEN}`,
        },
        timeout: 60000, // some models take time
      }
    );

    // Hugging Face returns a plain text output, we need to extract JSON from it
    const text = hfResponse.data?.[0]?.generated_text || "";
    console.log("HF response text:", text);

    // Try to extract and parse the JSON array from the response
    const jsonStart = text.indexOf("[");
    const jsonEnd = text.lastIndexOf("]");
    let recipes = [];

    if (jsonStart !== -1 && jsonEnd !== -1) {
      const jsonStr = text.substring(jsonStart, jsonEnd + 1);
      recipes = JSON.parse(jsonStr);
    } else {
      return res.status(500).json({ error: "Failed to parse recipe data from model" });
    }

    // Add dummy _id for frontend use
    const recipesWithId = recipes.map((recipe, index) => ({
      _id: `hf-${Date.now()}-${index}`,
      ...recipe,
    }));

    res.json({ recipes: recipesWithId });

  } catch (error) {
    console.error("Hugging Face Error:", error.message);
    res.status(500).json({ error: "Server error while generating recipes" });
  }
});

module.exports = router;