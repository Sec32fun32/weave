"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[795],{6517:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>c,contentTitle:()=>r,default:()=>p,frontMatter:()=>s,metadata:()=>i,toc:()=>d});var a=t(5893),o=t(1151);const s={},r="Tracing",i={id:"guides/tracking/tracing",title:"Tracing",description:"Tracing is a powerful feature in Weave that allows you to track the inputs and outputs of functions seamlessly. Follow these steps to get started:",source:"@site/docs/guides/tracking/tracing.md",sourceDirName:"guides/tracking",slug:"/guides/tracking/tracing",permalink:"/weave/guides/tracking/tracing",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/tracking/tracing.md",tags:[],version:"current",frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Ops",permalink:"/weave/guides/tracking/ops"},next:{title:"Feedback",permalink:"/weave/guides/tracking/feedback"}},c={},d=[{value:"Add additional attributes",id:"add-additional-attributes",level:2}];function l(e){const n={code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",...(0,o.a)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(n.h1,{id:"tracing",children:"Tracing"}),"\n",(0,a.jsx)(n.p,{children:"Tracing is a powerful feature in Weave that allows you to track the inputs and outputs of functions seamlessly. Follow these steps to get started:"}),"\n",(0,a.jsx)(n.p,{children:"To track specific functions, decorate them with @weave.op(). This decorator tells Weave to monitor the inputs, outputs, and any code changes for the function. Now, every call to this function will be tracked and logged. Additionally, weave tracks how functions relate by keeping track of parent and children calls and building a trace tree."}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'# highlight-next-line\nimport weave\nfrom openai import OpenAI\nimport requests, random\nPROMPT="""Emulate the Pokedex from early Pok\xe9mon episodes. State the name of the Pokemon and then describe it.\n        Your tone is informative yet sassy, blending factual details with a touch of dry humor. Be concise, no more than 3 sentences. """\nPOKEMON = [\'pikachu\', \'charmander\', \'squirtle\', \'bulbasaur\', \'jigglypuff\', \'meowth\', \'eevee\']\n\n# highlight-next-line\n@weave.op()\ndef get_pokemon_data(pokemon_name):\n    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"\n    response = requests.get(url)\n    if response.status_code == 200:\n        data = response.json()\n        name = data["name"]\n        types = [t["type"]["name"] for t in data["types"]]\n        species_url = data["species"]["url"]\n        species_response = requests.get(species_url)\n        evolved_from = "Unknown"\n        if species_response.status_code == 200:\n            species_data = species_response.json()\n            if species_data["evolves_from_species"]:\n                evolved_from = species_data["evolves_from_species"]["name"]\n        return {"name": name, "types": types, "evolved_from": evolved_from}\n    else:\n        return None\n\n# highlight-next-line\n@weave.op()\ndef pokedex(name: str, prompt: str) -> str:\n    client = OpenAI()\n    data = get_pokemon_data(name)\n    if not data: return "Error: Unable to fetch data"\n    response = client.chat.completions.create(\n        model="gpt-3.5-turbo",\n        messages=[\n            {"role": "system","content": prompt},\n            {"role": "user", "content": str(data)}\n        ],\n        temperature=0.7,\n        max_tokens=100,\n        top_p=1\n    )\n    return response.choices[0].message.content\n\n# highlight-next-line\nweave.init(\'intro-example\')\n# Get data for a specific Pok\xe9mon\npokemon_data = pokedex(random.choice(POKEMON), PROMPT)\n'})}),"\n",(0,a.jsx)(n.h2,{id:"add-additional-attributes",children:"Add additional attributes"}),"\n",(0,a.jsxs)(n.p,{children:["When calling tracked functions, you can add additional metadata to the call by using the ",(0,a.jsx)(n.code,{children:"weave.attributes"})," context manager."]}),"\n",(0,a.jsxs)(n.p,{children:["For example, you can add a ",(0,a.jsx)(n.code,{children:"user_id"})," to each call and then filter calls by user. In the example below, any function called within the context manager will have the ",(0,a.jsx)(n.code,{children:"user_id"})," attribute set to ",(0,a.jsx)(n.code,{children:"lukas"})," and ",(0,a.jsx)(n.code,{children:"env"})," attribute set to ",(0,a.jsx)(n.code,{children:"production"}),"."]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import weave\nimport json\nfrom openai import OpenAI\n\n@weave.op()\ndef extract_fruit(sentence: str) -> dict:\n    client = OpenAI()\n\n    response = client.chat.completions.create(\n    model="gpt-3.5-turbo-1106",\n    messages=[\n        {\n            "role": "system",\n            "content": "You will be provided with unstructured data, and your task is to parse it one JSON dictionary with fruit, color and flavor as keys."\n        },\n        {\n            "role": "user",\n            "content": sentence\n        }\n        ],\n        temperature=0.7,\n        response_format={ "type": "json_object" }\n    )\n    extracted = response.choices[0].message.content\n    return json.loads(extracted)\n\nweave.init(\'intro-example\')\nsentence = "There are many fruits that were found on the recently discovered planet Goocrux. There are neoskizzles that grow there, which are purple and taste like candy."\n\n# highlight-next-line\nwith weave.attributes({\'user_id\': \'lukas\', \'env\': \'production\'}):\n    extract_fruit(sentence)\n'})})]})}function p(e={}){const{wrapper:n}={...(0,o.a)(),...e.components};return n?(0,a.jsx)(n,{...e,children:(0,a.jsx)(l,{...e})}):l(e)}},1151:(e,n,t)=>{t.d(n,{Z:()=>i,a:()=>r});var a=t(7294);const o={},s=a.createContext(o);function r(e){const n=a.useContext(s);return a.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function i(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:r(e.components),a.createElement(s.Provider,{value:n},e.children)}}}]);