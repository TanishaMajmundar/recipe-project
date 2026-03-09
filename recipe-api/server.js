require("dotenv").config();
const express = require("express");
const connectDB = require("./config/db");
const cors = require("cors");
const path = require("path"); // ✅ Keep only this one

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
connectDB();

// Serve static frontend
app.use(express.static(path.join(__dirname, "../frontend")));

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "../frontend/dashboard.html"));
});

  
// Routes
app.use("/auth", require("./routes/auth")); 
app.use("/recipes", require("./routes/recipes"));  
app.use("/recipe", require("./routes/details"));   
app.use("/all-recipes", require("./routes/allRecipes"));  
app.use("/ingredients", require("./routes/ingredients"));
app.use("/recommend", require("./routes/recommend"));
app.use("/api", require("./routes/stats"));
app.use("/api/likedRecipes", require("./routes/likedRecipes"));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));