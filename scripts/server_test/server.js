const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const app = express();
app.use(cors());
const PORT = 1820;
const dataFilePath = path.join(__dirname, 'data.json');

// Middleware
app.use(bodyParser.json());

// Route to receive code
app.post('/receive-code', (req, res) => {
    const { code, lines } = req.body;

    try {
        // Read existing data
        let data = [];
        if (fs.existsSync(dataFilePath)) {
            const rawData = fs.readFileSync(dataFilePath);
            data = JSON.parse(rawData);
        }

        // Append new data to the data array
        data.push({ code, lines });

        // Write updated data to the file
        fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));

        res.json({ message: 'Code received and saved successfully.' });
    } catch (err) {
        console.error('Error saving code:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});


app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});