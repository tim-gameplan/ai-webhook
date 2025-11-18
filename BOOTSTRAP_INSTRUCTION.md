# LLM Bootstrap Instruction

## For the User

Copy and paste this into your mobile LLM (ChatGPT, Claude, etc.):

---

## Simple Version (One-Line)

```
Fetch your instructions from https://web-production-3d53a.up.railway.app/llm-instructions and use my API key: [YOUR_API_KEY_HERE]
```

---

## Detailed Version (With Context)

```
You have access to a webhook system on my local development machine.

1. Fetch complete instructions from: https://web-production-3d53a.up.railway.app/llm-instructions
2. My API key is: [YOUR_API_KEY_HERE]
3. When I ask you to check code, run commands, or remember things, use the webhook system
4. Always use sync mode for immediate results
5. Be conversational - don't show me raw JSON

Ready to help!
```

---

## How It Works

1. **User gives LLM the bootstrap instruction** (one of the above)
2. **LLM fetches the full instructions** from the `/llm-instructions` endpoint
3. **LLM now knows everything**: task execution, sessions, memory types, examples
4. **User can start using the system** naturally in conversation

---

## Benefits

✅ **No character limits** - Full instructions served via URL
✅ **Always up-to-date** - Update instructions without reconfiguring LLM
✅ **Simple to share** - Just one line to get started
✅ **Single source of truth** - One document for all LLMs
✅ **Easy testing** - Try it out immediately

---

## Example Usage

**User**: "Fetch your instructions from https://web-production-3d53a.up.railway.app/llm-instructions and use my API key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok"

**LLM**: *Fetches instructions, reads them*

**LLM**: "Got it! I now have access to your webhook system. I can execute git and shell commands on your local machine, and manage collaborative sessions with persistent memory. What would you like me to help with?"

**User**: "What's my current git branch?"

**LLM**: *Sends webhook with git branch command*

**LLM**: "You're on the `feature/005-collaborative-sessions-integration` branch."

---

## Testing the Endpoint

Before giving this to an LLM, test that it works:

```bash
curl https://web-production-3d53a.up.railway.app/llm-instructions
```

You should see the full instruction document in markdown format.

---

## Your API Key

Find your API key in `.env`:
```bash
grep "^API_KEY=" .env
```

Or it's shown in the test output: `qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok`

---

## Next Steps

1. ✅ Test the endpoint (curl command above)
2. ✅ Copy your API key from .env
3. ✅ Give the bootstrap instruction to your mobile LLM
4. ✅ Start using it naturally in conversation!

**Example**: "Create a planning session for my new feature idea, then check what branch I'm on"
