# 🔑 How to Get and Configure Your Anthropic API Key

## Step 1: Get Your API Key from Anthropic

1. **Go to:** https://console.anthropic.com/
2. **Sign in** to your Anthropic account
3. **Navigate to:** Settings → API Keys
4. **Click:** "Create Key" or copy an existing key
5. **Copy** the key (starts with `sk-ant-`)

## Step 2: Configure the Backend

### Option A: Quick Update (Recommended)
```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend

# Update the .env file
sed -i '' 's/API_KEY=sk-ant-test-key-placeholder/API_KEY=YOUR_KEY_HERE/' .env
```

### Option B: Manual Edit
```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend
nano .env

# Change this line:
API_KEY=sk-ant-test-key-placeholder

# To:
API_KEY=sk-ant-your-actual-key-here

# Save: Ctrl+O, Enter, Ctrl+X
```

## Step 3: Restart Backend

```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend

# Kill current backend
pkill -9 uvicorn

# Restart with new key
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Test AI Suggestions

1. Open http://localhost:5173
2. Login to your account
3. Go to Visualize page
4. Select a dataset
5. Click "Get AI Suggestions"
6. Should now receive 3-5 AI-powered chart recommendations!

---

## Alternative: Use Environment Variable

If you prefer not to store the key in the file:

```bash
export API_KEY="sk-ant-your-key-here"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

## Verify It's Working

Test the API directly:
```bash
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@insightforge.com","password":"testpass123"}' | jq -r '.access_token')

DATASET_ID="your-dataset-id"

curl -X POST "http://localhost:8000/api/visualize/suggest?dataset_id=$DATASET_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Should return JSON with chart suggestions instead of an error!

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your API key to git
- The `.env` file is in `.gitignore` (safe)
- Keep your key private
- Rotate keys if accidentally exposed

---

## What Changes After Adding the Key?

✅ **Will Work:**
- AI-powered visualization suggestions
- Intelligent chart type recommendations
- Confidence scores for each suggestion
- Reasoning for why each chart is suggested

✅ **Still Works (no key needed):**
- Manual chart creation
- All chart types
- Dataset upload/preview
- User authentication

---

## Need Help?

If you get errors after adding the key:
1. Check the key format (should start with `sk-ant-`)
2. Verify no extra spaces or quotes
3. Check backend logs: `tail -f /tmp/backend.log`
4. Restart backend server

---

**Ready to add your key?** Follow the steps above! 🚀
