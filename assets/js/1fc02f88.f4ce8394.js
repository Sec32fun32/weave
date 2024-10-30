"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[636],{99354:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>i,default:()=>u,frontMatter:()=>a,metadata:()=>r,toc:()=>d});var s=n(85893),o=n(11151);const a={},i="Ops",r={id:"guides/tracking/ops",title:"Ops",description:"A Weave op is a versioned function that automatically logs all calls.",source:"@site/docs/guides/tracking/ops.md",sourceDirName:"guides/tracking",slug:"/guides/tracking/ops",permalink:"/guides/tracking/ops",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/tracking/ops.md",tags:[],version:"current",lastUpdatedAt:1730319461e3,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Calls",permalink:"/guides/tracking/tracing"},next:{title:"Objects",permalink:"/guides/tracking/objects"}},c={},d=[{value:"Customize display names",id:"customize-display-names",level:2},{value:"Customize logged inputs and outputs",id:"customize-logged-inputs-and-outputs",level:2}];function p(e){const t={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",...(0,o.a)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(t.h1,{id:"ops",children:"Ops"}),"\n",(0,s.jsx)(t.p,{children:"A Weave op is a versioned function that automatically logs all calls."}),"\n",(0,s.jsxs)(t.p,{children:["To create an op, decorate a python function with ",(0,s.jsx)(t.code,{children:"weave.op()"})]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:"import weave\n\n@weave.op()\ndef track_me(v):\n    return v + 5\n\nweave.init('intro-example')\ntrack_me(15)\n"})}),"\n",(0,s.jsx)(t.p,{children:"Calling an op will create a new op version if the code has changed from the last call, and log the inputs and outputs of the function."}),"\n",(0,s.jsx)(t.admonition,{type:"note",children:(0,s.jsxs)(t.p,{children:["Functions decorated with ",(0,s.jsx)(t.code,{children:"@weave.op()"})," will behave normally (without code versioning and tracking), if you don't call ",(0,s.jsx)(t.code,{children:"weave.init('your-project-name')"})," before calling them."]})}),"\n",(0,s.jsxs)(t.p,{children:["Ops can be ",(0,s.jsx)(t.a,{href:"/guides/tools/serve",children:"served"})," or ",(0,s.jsx)(t.a,{href:"/guides/tools/deploy",children:"deployed"})," using the Weave toolbelt."]}),"\n",(0,s.jsx)(t.h2,{id:"customize-display-names",children:"Customize display names"}),"\n",(0,s.jsxs)(t.p,{children:["You can customize the op's display name by setting the ",(0,s.jsx)(t.code,{children:"name"})," parameter in the ",(0,s.jsx)(t.code,{children:"@weave.op"})," decorator:"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:'@weave.op(name="custom_name")\ndef func():\n    ...\n'})}),"\n",(0,s.jsx)(t.h2,{id:"customize-logged-inputs-and-outputs",children:"Customize logged inputs and outputs"}),"\n",(0,s.jsxs)(t.p,{children:["If you want to change the data that is logged to weave without modifying the original function (e.g. to hide sensitive data), you can pass ",(0,s.jsx)(t.code,{children:"postprocess_inputs"})," and ",(0,s.jsx)(t.code,{children:"postprocess_output"})," to the op decorator."]}),"\n",(0,s.jsxs)(t.p,{children:[(0,s.jsx)(t.code,{children:"postprocess_inputs"})," takes in a dict where the keys are the argument names and the values are the argument values, and returns a dict with the transformed inputs."]}),"\n",(0,s.jsxs)(t.p,{children:[(0,s.jsx)(t.code,{children:"postprocess_output"})," takes in any value which would normally be returned by the function and returns the transformed output."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-py",children:'from dataclasses import dataclass\nfrom typing import Any\nimport weave\n\n@dataclass\nclass CustomObject:\n    x: int\n    secret_password: str\n\ndef postprocess_inputs(inputs: dict[str, Any]) -> dict[str, Any]:\n    return {k:v for k,v in inputs.items() if k != "hide_me"}\n\ndef postprocess_output(output: CustomObject) -> CustomObject:\n    return CustomObject(x=output.x, secret_password="REDACTED")\n\n@weave.op(\n    postprocess_inputs=postprocess_inputs,\n    postprocess_output=postprocess_output,\n)\ndef func(a: int, hide_me: str) -> CustomObject:\n    return CustomObject(x=a, secret_password=hide_me)\n\nweave.init(\'hide-data-example\') # \ud83d\udc1d\nfunc(a=1, hide_me="password123")\n'})})]})}function u(e={}){const{wrapper:t}={...(0,o.a)(),...e.components};return t?(0,s.jsx)(t,{...e,children:(0,s.jsx)(p,{...e})}):p(e)}},11151:(e,t,n)=>{n.d(t,{Z:()=>r,a:()=>i});var s=n(67294);const o={},a=s.createContext(o);function i(e){const t=s.useContext(a);return s.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:i(e.components),s.createElement(a.Provider,{value:t},e.children)}}}]);