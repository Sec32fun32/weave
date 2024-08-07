"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[53],{1109:e=>{e.exports=JSON.parse('{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"documentationSidebar":[{"type":"category","collapsible":true,"collapsed":false,"label":"Getting Started","items":[{"type":"link","label":"Introduction","href":"/weave/","docId":"introduction","unlisted":false},{"type":"link","label":"Track LLM inputs & outputs","href":"/weave/quickstart","docId":"quickstart","unlisted":false},{"type":"link","label":"Track data flows and app metadata","href":"/weave/tutorial-tracing_2","docId":"tutorial-tracing_2","unlisted":false},{"type":"link","label":"App versioning","href":"/weave/tutorial-weave_models","docId":"tutorial-weave_models","unlisted":false},{"type":"link","label":"Tutorial: Build an Evaluation pipeline","href":"/weave/tutorial-eval","docId":"tutorial-eval","unlisted":false},{"type":"link","label":"Tutorial: Model-Based Evaluation of RAG applications","href":"/weave/tutorial-rag","docId":"tutorial-rag","unlisted":false}]},{"type":"category","collapsible":true,"collapsed":false,"label":"Using Weave","items":[{"type":"category","collapsible":true,"collapsed":false,"label":"Core Types","items":[{"type":"link","label":"Models","href":"/weave/guides/core-types/models","docId":"guides/core-types/models","unlisted":false},{"type":"link","label":"Datasets","href":"/weave/guides/core-types/datasets","docId":"guides/core-types/datasets","unlisted":false},{"type":"link","label":"Evaluation","href":"/weave/guides/core-types/evaluations","docId":"guides/core-types/evaluations","unlisted":false}],"href":"/weave/guides/core-types/"},{"type":"category","collapsible":true,"collapsed":false,"label":"Tracking","items":[{"type":"link","label":"Objects","href":"/weave/guides/tracking/objects","docId":"guides/tracking/objects","unlisted":false},{"type":"link","label":"Ops","href":"/weave/guides/tracking/ops","docId":"guides/tracking/ops","unlisted":false},{"type":"link","label":"Tracing","href":"/weave/guides/tracking/tracing","docId":"guides/tracking/tracing","unlisted":false},{"type":"link","label":"Feedback","href":"/weave/guides/tracking/feedback","docId":"guides/tracking/feedback","unlisted":false}],"href":"/weave/guides/tracking/"},{"type":"category","collapsible":true,"collapsed":true,"label":"Integrations","items":[{"type":"link","label":"OpenAI","href":"/weave/guides/integrations/openai","docId":"guides/integrations/openai","unlisted":false},{"type":"link","label":"Anthropic","href":"/weave/guides/integrations/anthropic","docId":"guides/integrations/anthropic","unlisted":false},{"type":"link","label":"Cohere","href":"/weave/guides/integrations/cohere","docId":"guides/integrations/cohere","unlisted":false},{"type":"link","label":"MistralAI","href":"/weave/guides/integrations/mistral","docId":"guides/integrations/mistral","unlisted":false},{"type":"link","label":"LangChain","href":"/weave/guides/integrations/langchain","docId":"guides/integrations/langchain","unlisted":false},{"type":"link","label":"LlamaIndex","href":"/weave/guides/integrations/llamaindex","docId":"guides/integrations/llamaindex","unlisted":false},{"type":"link","label":"DSPy","href":"/weave/guides/integrations/dspy","docId":"guides/integrations/dspy","unlisted":false},{"type":"link","label":"Google Gemini","href":"/weave/guides/integrations/google-gemini","docId":"guides/integrations/google-gemini","unlisted":false},{"type":"link","label":"Together AI","href":"/weave/guides/integrations/together_ai","docId":"guides/integrations/together_ai","unlisted":false},{"type":"link","label":"Groq","href":"/weave/guides/integrations/groq","docId":"guides/integrations/groq","unlisted":false},{"type":"link","label":"Open Router","href":"/weave/guides/integrations/openrouter","docId":"guides/integrations/openrouter","unlisted":false},{"type":"link","label":"Local Models","href":"/weave/guides/integrations/local_models","docId":"guides/integrations/local_models","unlisted":false},{"type":"link","label":"LiteLLM","href":"/weave/guides/integrations/litellm","docId":"guides/integrations/litellm","unlisted":false}],"href":"/weave/guides/integrations/"},{"type":"category","collapsible":true,"collapsed":true,"label":"Tools","items":[{"type":"link","label":"Serve","href":"/weave/guides/tools/serve","docId":"guides/tools/serve","unlisted":false},{"type":"link","label":"Deploy","href":"/weave/guides/tools/deploy","docId":"guides/tools/deploy","unlisted":false}],"href":"/weave/guides/tools/"},{"type":"link","label":"Platform & Security","href":"/weave/guides/platform/","docId":"guides/platform/index","unlisted":false}]},{"type":"link","label":"API Reference","href":"/api-reference/python/weave"}],"apiReferenceSidebar":[{"type":"category","label":"Python API","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"weave","href":"/weave/api-reference/python/weave","docId":"api-reference/python/weave","unlisted":false}],"href":"/weave/category/python-api"}]},"docs":{"api-reference/python/weave":{"id":"api-reference/python/weave","title":"weave","description":"These are the top-level functions in the import weave namespace.","sidebar":"apiReferenceSidebar"},"guides/core-types/datasets":{"id":"guides/core-types/datasets","title":"Datasets","description":"Datasets enable you to collect examples for evaluation and automatically track versions for accurate comparisons. Use this to download the latest version locally with a simple API.","sidebar":"documentationSidebar"},"guides/core-types/evaluations":{"id":"guides/core-types/evaluations","title":"Evaluation","description":"Evaluation-driven development helps you reliably iterate on an application. The Evaluation class is designed to assess the performance of a Model on a given Dataset or set of examples using scoring functions.","sidebar":"documentationSidebar"},"guides/core-types/index":{"id":"guides/core-types/index","title":"Weave Core Types","description":"Weave Core Types are built with weave tracking, and contain everything you need to rapidly iterate on AI projects.","sidebar":"documentationSidebar"},"guides/core-types/models":{"id":"guides/core-types/models","title":"Models","description":"A Model is a combination of data (which can include configuration, trained model weights, or other information) and code that defines how the model operates. By structuring your code to be compatible with this API, you benefit from a structured way to version your application so you can more systematically keep track of your experiments.","sidebar":"documentationSidebar"},"guides/integrations/anthropic":{"id":"guides/integrations/anthropic","title":"Anthropic","description":"Weave automatically tracks and logs LLM calls made via the Anthropic Python library, after weave.init() is called.","sidebar":"documentationSidebar"},"guides/integrations/cohere":{"id":"guides/integrations/cohere","title":"Cohere","description":"Weave automatically tracks and logs LLM calls made via the Cohere Python library after weave.init() is called.","sidebar":"documentationSidebar"},"guides/integrations/dspy":{"id":"guides/integrations/dspy","title":"DSPy","description":"DSPy is a framework for algorithmically optimizing LM prompts and weights, especially when LMs are used one or more times within a pipeline. Weave automatically tracks and logs calls made using DSPy modules and functions.","sidebar":"documentationSidebar"},"guides/integrations/google-gemini":{"id":"guides/integrations/google-gemini","title":"Google Gemini","description":"Google offers two ways of calling Gemini via API:","sidebar":"documentationSidebar"},"guides/integrations/groq":{"id":"guides/integrations/groq","title":"Groq","description":"Groq is the AI infrastructure company that delivers fast AI inference. The LPU\u2122 Inference Engine by Groq is a hardware and software platform that delivers exceptional compute speed, quality, and energy efficiency. Weave automatically tracks and logs calls made using Groq chat completion calls.","sidebar":"documentationSidebar"},"guides/integrations/index":{"id":"guides/integrations/index","title":"Weave Integrations","description":"Weave contains automatic logging integrations for popular LLMs and orchestration frameworks. Weave will automatically trace calls made via the following libraries:","sidebar":"documentationSidebar"},"guides/integrations/langchain":{"id":"guides/integrations/langchain","title":"LangChain","description":"Weave is designed to make tracking and logging all calls made through the LangChain Python library effortless.","sidebar":"documentationSidebar"},"guides/integrations/litellm":{"id":"guides/integrations/litellm","title":"LiteLLM","description":"Weave automatically tracks and logs LLM calls made via LiteLLM, after weave.init() is called.","sidebar":"documentationSidebar"},"guides/integrations/llamaindex":{"id":"guides/integrations/llamaindex","title":"LlamaIndex","description":"Weave is designed to simplify the tracking and logging of all calls made through the LlamaIndex Python library.","sidebar":"documentationSidebar"},"guides/integrations/local_models":{"id":"guides/integrations/local_models","title":"Local Models","description":"Many developers download and run open source models like LLama-3, Mixtral, Gemma, Phi and more locally. There are quite a few ways of running these models locally and Weave supports a few of them out of the box, as long as they support OpenAI SDK compatibility.","sidebar":"documentationSidebar"},"guides/integrations/mistral":{"id":"guides/integrations/mistral","title":"MistralAI","description":"Weave automatically tracks and logs LLM calls made via the MistralAI Python library.","sidebar":"documentationSidebar"},"guides/integrations/openai":{"id":"guides/integrations/openai","title":"OpenAI","description":"Tracing","sidebar":"documentationSidebar"},"guides/integrations/openrouter":{"id":"guides/integrations/openrouter","title":"Open Router","description":"Openrouter.ai is a unified interface for many LLMs, supporting both foundational models like OpenAI GPT-4, Anthropic Claude, Google Gemini but also open source models like LLama-3, Mixtral and many more, some models are even offered for free.","sidebar":"documentationSidebar"},"guides/integrations/together_ai":{"id":"guides/integrations/together_ai","title":"Together AI","description":"Together AI is a platform for building and finetuning generative AI models, focusing on Open Source LLMs, and allowing customers to fine-tune and host their own models.","sidebar":"documentationSidebar"},"guides/platform/index":{"id":"guides/platform/index","title":"Platform & Security","description":"Weave is available on W&B SaaS Cloud which is a multi-tenant, fully-managed platform deployed in W&B\'s Google Cloud Platform (GCP) account in a North America region.","sidebar":"documentationSidebar"},"guides/tools/deploy":{"id":"guides/tools/deploy","title":"Deploy","description":"Deploy to GCP","sidebar":"documentationSidebar"},"guides/tools/index":{"id":"guides/tools/index","title":"Tools","description":"- serve: Serve Weave ops and models","sidebar":"documentationSidebar"},"guides/tools/serve":{"id":"guides/tools/serve","title":"Serve","description":"Given a Weave ref to any Weave Model you can run:","sidebar":"documentationSidebar"},"guides/tracking/feedback":{"id":"guides/tracking/feedback","title":"Feedback","description":"Evaluating LLM applications automatically is challenging. Teams often rely on direct user feedback, particularly from domain experts, who assess the content quality using simple indicators such as thumbs up or down. Developers also actively identify and resolve content issues.","sidebar":"documentationSidebar"},"guides/tracking/index":{"id":"guides/tracking/index","title":"Tracking","description":"Weave track and versions objects and function calls.","sidebar":"documentationSidebar"},"guides/tracking/objects":{"id":"guides/tracking/objects","title":"Objects","description":"Weave\'s serialization layer saves and versions Python objects.","sidebar":"documentationSidebar"},"guides/tracking/ops":{"id":"guides/tracking/ops","title":"Ops","description":"A Weave op is a versioned function that automatically logs all calls.","sidebar":"documentationSidebar"},"guides/tracking/tracing":{"id":"guides/tracking/tracing","title":"Tracing","description":"Tracing is a powerful feature in Weave that allows you to track the inputs and outputs of functions seamlessly. Follow these steps to get started:","sidebar":"documentationSidebar"},"introduction":{"id":"introduction","title":"Introduction","description":"Weave is a lightweight toolkit for tracking and evaluating LLM applications, built by Weights & Biases.","sidebar":"documentationSidebar"},"quickstart":{"id":"quickstart","title":"Track LLM inputs & outputs","description":"Follow these steps to track your first call or","sidebar":"documentationSidebar"},"tutorial-eval":{"id":"tutorial-eval","title":"Tutorial: Build an Evaluation pipeline","description":"To iterate on an application, we need a way to evaluate if it\'s improving. To do so, a common practice is to test it against the same set of examples when there is a change. Weave has a first-class way to track evaluations with Model & Evaluation classes. We have built the APIs to make minimal assumptions to allow for the flexibility to support a wide array of use-cases.","sidebar":"documentationSidebar"},"tutorial-rag":{"id":"tutorial-rag","title":"Tutorial: Model-Based Evaluation of RAG applications","description":"Retrieval Augmented Generation (RAG) is a common way of building Generative AI applications that have access to custom knowledge bases.","sidebar":"documentationSidebar"},"tutorial-tracing_2":{"id":"tutorial-tracing_2","title":"Track data flows and app metadata","description":"In the Track LLM inputs & outputs tutorial, the basics of tracking the inputs and outputs of your LLMs was covered.","sidebar":"documentationSidebar"},"tutorial-weave_models":{"id":"tutorial-weave_models","title":"App versioning","description":"Tracking the inputs, outputs, metadata as well as data flowing through your app is critical to understanding the performance of your system. However versioning your app over time is also critical to understand how modifications to your code or app attributes change your outputs. Weave\'s Model class is how these changes can be tracked in Weave.","sidebar":"documentationSidebar"}}}')}}]);