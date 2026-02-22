#cd backend
#python3 -c "
import asyncio, os
from dotenv import load_dotenv
load_dotenv()
import anthropic

async def test():
    client = anthropic.AsyncAnthropic()
    # grab one persona
    with open('data/processed/manifest.json') as f:
        import json; manifest = json.load(f)
    first_key = list(manifest.keys())[0]
    persona_path = manifest[first_key]['persona_file']
    fixed_path = persona_path.replace('backend/', '', 1) if persona_path.startswith('backend/') else persona_path
    with open(fixed_path) as f:
        persona = f.read()
    
    resp = await client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=500,
        system=persona,
        messages=[{'role':'user','content':'H&M is launching oversized graphic t-shirts with 90s vintage designs at €24.99. What is your honest reaction?'}]
    )
    print('PERSONA (first 200 chars):', persona[:200])
    print()
    print('RESPONSE:', resp.content[0].text)

asyncio.run(test())
#"