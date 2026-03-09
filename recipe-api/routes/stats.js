const express = require('express');
const router = express.Router();
const User = require('../models/User');
const Recipe = require('../models/Recipe');

router.get('/stats', async (req, res) => {
    try {
        const userCount = await User.countDocuments();
        const recipeCount = await Recipe.countDocuments();
        res.json({ users: userCount, recipes: recipeCount });
    } catch (error) {
        console.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

module.exports = router;