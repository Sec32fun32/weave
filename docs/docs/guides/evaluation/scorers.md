import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Evaluation Metrics

## Evaluations in Weave

In Weave, Scorers are used to evaluate AI outputs and return evaluation metrics. They take the AI's output, analyze it, and return a dictionary of results. Scorers can use your input data as reference if needed and can also output extra information, such as explanations or reasonings from the evaluation.

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    Scorers are passed to a `weave.Evaluation` object during evaluation. There are two types of Scorers in weave:

    1. **Function-based Scorers:** Simple Python functions decorated with `@weave.op`.
    2. **Class-based Scorers:** Python classes that inherit from `weave.Scorer` for more complex evaluations.

    Scorers must return a dictionary and can return multiple metrics, nested metrics and non-numeric values such as text returned from a LLM-evaluator about its reasoning.

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    Scorers are special ops passed to a `weave.Evaluation` object during evaluation.
  </TabItem>
</Tabs>

## Create your own Scorers

### Function-based Scorers

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    These are functions decorated with `@weave.op` that return a dictionary. They're great for simple evaluations like:

    ```python
    import weave

    @weave.op
    def evaluate_uppercase(text: str) -> dict:
        return {"text_is_uppercase": text.isupper()}

    my_eval = weave.Evaluation(
        dataset=[{"text": "HELLO WORLD"}],
        scorers=[evaluate_uppercase]
    )
    ```

    When the evaluation is run, `evaluate_uppercase` checks if the text is all uppercase.

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    These are functions wrapped with `weave.op` that accept an object with `modelOutput` and optionally `datasetRow`.  They're great for simple evaluations like:
    ```typescript
    import * as weave from 'weave'

    const evaluateUppercase = weave.op(
        ({modelOutput}) => modelOutput.toUpperCase() === modelOutput,
        {name: 'textIsUppercase'}
    );


    const myEval = new weave.Evaluation({
        dataset: [{text: 'HELLO WORLD'}],
        scorers: [evaluateUppercase],
    })
    ```

  </TabItem>
</Tabs>

### Class-based Scorers

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    For more advanced evaluations, especially when you need to keep track of additional scorer metadata, try different prompts for your LLM-evaluators, or make multiple function calls, you can use the `Scorer` class.

    **Requirements:**

    1. Inherit from `weave.Scorer`.
    2. Define a `score` method decorated with `@weave.op`.
    3. The `score` method must return a dictionary.

    Example:

    ```python
    import weave
    from openai import OpenAI
    from weave import Scorer

    llm_client = OpenAI()

    #highlight-next-line
    class SummarizationScorer(Scorer):
        model_id: str = "gpt-4o"
        system_prompt: str = "Evaluate whether the summary is good."

        @weave.op
        def some_complicated_preprocessing(self, text: str) -> str:
            processed_text = "Original text: \n" + text + "\n"
            return processed_text

        @weave.op
        def call_llm(self, summary: str, processed_text: str) -> dict:
            res = llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": (
                        f"Analyse how good the summary is compared to the original text."
                        f"Summary: {summary}\n{processed_text}"
                    )}])
            return {"summary_quality": res}

        @weave.op
        def score(self, output: str, text: str) -> dict:
            """Score the summary quality.

            Args:
                output: The summary generated by an AI system
                text: The original text being summarized
            """
            processed_text = self.some_complicated_preprocessing(text)
            eval_result = self.call_llm(summary=output, processed_text=processed_text)
            return {"summary_quality": eval_result}

    evaluation = weave.Evaluation(
        dataset=[{"text": "The quick brown fox jumps over the lazy dog."}],
        scorers=[summarization_scorer])
    ```

    This class evaluates how good a summary is by comparing it to the original text.

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    ```plaintext
    This feature is not available in TypeScript yet.  Stay tuned!
    ```
  </TabItem>
</Tabs>

## How Scorers Work

### Scorer Keyword Arguments

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    Scorers can access both the output from your AI system and the input data from the dataset row.

    - **Input:** If you would like your scorer to use data from your dataset row, such as a "label" or "target" column then you can easily make this available to the scorer by adding a `label` or `target` keyword argument to your scorer definition.

    For example if you wanted to use a column called "label" from your dataset then your scorer function (or `score` class method) would have a parameter list like this:

    ```python
    @weave.op
    def my_custom_scorer(output: str, label: int) -> dict:
        ...
    ```

    When a weave `Evaluation` is run, the output of the AI system is passed to the `output` parameter. The `Evaluation` also automatically tries to match any additional scorer argument names to your dataset columns. If customizing your scorer arguments or dataset columns is not feasible, you can use column mapping - see below for more.

    - **Output:** Include an `output` parameter in your scorer function's signature to access the AI system's output.

    ### Mapping Column Names with `column_map`

    Sometimes, the `score` methods' argument names don't match the column names in your dataset. You can fix this using a `column_map`.

    If you're using a class-based scorer, pass a dictionary to the `column_map` attribute of `Scorer` when you initialise your scorer class. This dictionary maps your `score` method's argument names to the dataset's column names, in the order: `{scorer_keyword_argument: dataset_column_name}`.

    Example:

    ```python
    import weave
    from weave import Scorer

    # A dataset with news articles to be summarised
    dataset = [
        {"news_article": "The news today was great...", "date": "2030-04-20", "source": "Bright Sky Network"},
        ...
    ]

    # Scorer class
    class SummarizationScorer(Scorer):

        @weave.op
        def score(output, text) -> dict:
            """
                output: output summary from a LLM summarization system
                text: the text being summarised
            """
            ...  # evaluate the quality of the summary

    # create a scorer with a column mapping the `text` argument to the `news_article` data column
    scorer = SummarizationScorer(column_map={"text" : "news_article"})
    ```

    Now, the `text` argument in the `score` method will receive data from the `news_article` dataset column.

    **Notes:**

    - Another equivalent option to map your columns is to subclass the `Scorer` and overload the `score` method mapping the columns explicitly.

    ```python
    import weave
    from weave import Scorer

    class MySummarizationScorer(SummarizationScorer):

        @weave.op
        def score(self, output: str, news_article: str) -> dict:  # Added type hints
            # overload the score method and map columns manually
            return super().score(output=output, text=news_article)
    ```

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    Scorers can access both the output from your AI system and the contents of the dataset row.

    You can easily access relevant columns from the dataset row by adding a `datasetRow` keyword argument to your scorer definition.

    ```typescript
    const myScorer = weave.op(
        ({modelOutput, datasetRow}) => {
            return modelOutput * 2 === datasetRow.expectedOutputTimesTwo;
        },
        {name: 'myScorer'}
    );
    ```

    ### Mapping Column Names with `columnMapping`
    :::warning

    In TypeScript, this feature is currently on the `Evaluation` object, not individual scorers!

    :::

    Sometimes your `datasetRow` keys will not exactly match the scorer's naming scheme, but they are semantically similar. You can map the columns using the `Evaluation`'s `columnMapping` option.

    The mapping is always from the scorer's perspective, i.e. `{scorer_key: dataset_column_name}`.

    Example:

    ```typescript
    const myScorer = weave.op(
        ({modelOutput, datasetRow}) => {
            return modelOutput * 2 === datasetRow.expectedOutputTimesTwo;
        },
        {name: 'myScorer'}
    );

    const myEval = new weave.Evaluation({
        dataset: [{expected: 2}],
        scorers: [myScorer],
        columnMapping: {expectedOutputTimesTwo: 'expected'}
    });
    ```

  </TabItem>
</Tabs>

### Final summarization of the scorer

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    During evaluation, the scorer will be computed for each row of your dataset. To provide a final score for the evaluation we provide an `auto_summarize` depending on the returning type of the output.
    - Averages are computed for numerical columns
    - Count and fraction for boolean columns
    - Other column types are ignored

    You can override the `summarize` method on the `Scorer` class and provide your own way of computing the final scores. The `summarize` function expects:

    - A single parameter `score_rows`: This is a list of dictionaries, where each dictionary contains the scores returned by the `score` method for a single row of your dataset.
    - It should return a dictionary containing the summarized scores.

    **Why this is useful?**

    When you need to score all rows before deciding on the final value of the score for the dataset.

    ```python
    class MyBinaryScorer(Scorer):
        """
        Returns True if the full output matches the target, False if not
        """

        @weave.op
        def score(output, target):
            return {"match": if output == target}

        def summarize(self, score_rows: list) -> dict:
            full_match = all(row["match"] for row in score_rows)
            return {"full_match": full_match}
    ```

    > In this example, the default `auto_summarize` would have returned the count and proportion of True.

    If you want to learn more, check the implementation of [CorrectnessLLMJudge](/tutorial-rag#optional-defining-a-scorer-class).

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    During evaluation, the scorer will be computed for each row of your dataset.  To provide a final score, we use an internal `summarizeResults` function that aggregates depending on the output type.
    - Averages are computed for numerical columns
    - Count and fraction for boolean columns
    - Other column types are ignored

    We don't currently support custom summarization.

  </TabItem>
</Tabs>

## Predefined Scorers

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>
    **Installation**

    To use Weave's predefined scorers you need to install some additional dependencies:

    ```bash
    pip install weave[scorers]
    ```

    **LLM-evaluators**

    The pre-defined scorers that use LLMs support the OpenAI, Anthropic, Google GenerativeAI and MistralAI clients. They also use `weave`'s `InstructorLLMScorer` class, so you'll need to install the [`instructor`](https://github.com/instructor-ai/instructor) Python package to be able to use them. You can get all necessary dependencies with `pip install "weave[scorers]"`

    ### `HallucinationFreeScorer`

    This scorer checks if your AI system's output includes any hallucinations based on the input data.

    ```python
    from weave.scorers import HallucinationFreeScorer

    llm_client = ... # initialize your LLM client here

    scorer = HallucinationFreeScorer(
        client=llm_client,
        model_id="gpt4o"
    )
    ```

    **Customization:**

    - Customize the `system_prompt` and `user_prompt` attributes of the scorer to define what "hallucination" means for you.

    **Notes:**

    - The `score` method expects an input column named `context`. If your dataset uses a different name, use the `column_map` attribute to map `context` to the dataset column.

    Here you have an example in the context of an evaluation:

    ```python
    import asyncio
    from openai import OpenAI
    import weave
    from weave.scorers import HallucinationFreeScorer

    # Initialize clients and scorers
    llm_client = OpenAI()
    hallucination_scorer = HallucinationFreeScorer(
        client=llm_client,
        model_id="gpt-4o",
        column_map={"context": "input", "output": "other_col"}
    )

    # Create dataset
    dataset = [
        {"input": "John likes various types of cheese."},
        {"input": "Pepe likes various types of cheese."},
    ]

    @weave.op
    def model(input: str) -> str:
        return "The person's favorite cheese is cheddar."

    # Run evaluation
    evaluation = weave.Evaluation(
        dataset=dataset,
        scorers=[hallucination_scorer],
    )
    result = asyncio.run(evaluation.evaluate(model))
    print(result)
    # {'HallucinationFreeScorer': {'has_hallucination': {'true_count': 2, 'true_fraction': 1.0}}, 'model_latency': {'mean': 1.4395725727081299}}
    ```

    ---

    ### `SummarizationScorer`

    Use an LLM to compare a summary to the original text and evaluate the quality of the summary.

    ```python
    from weave.scorers import SummarizationScorer

    llm_client = ... # initialize your LLM client here

    scorer = SummarizationScorer(
        client=llm_client,
        model_id="gpt4o"
    )
    ```

    **How It Works:**

    This scorer evaluates summaries in two ways:

    1. **Entity Density:** Checks the ratio of unique entities (like names, places, or things) mentioned in the summary to the total word count in the summary in order to estimate the "information density" of the summary. Uses an LLM to extract the entities. Similar to how entity density is used in the Chain of Density paper, https://arxiv.org/abs/2309.04269

    2. **Quality Grading:** Uses an LLM-evaluator to grade the summary as `poor`, `ok`, or `excellent`. These grades are converted to scores (0.0 for poor, 0.5 for ok, and 1.0 for excellent) so you can calculate averages.

    **Customization:**

    - Adjust `summarization_evaluation_system_prompt` and `summarization_evaluation_prompt` to define what makes a good summary.

    **Notes:**

    - This scorer uses the `InstructorLLMScorer` class.
    - The `score` method expects the original text that was summarized to be present in the `input` column of the dataset. Use the `column_map` class attribute to map `input` to the correct dataset column if needed.

    Here you have an example usage of the `SummarizationScorer` in the context of an evaluation:

    ```python
    import asyncio
    from openai import OpenAI
    import weave
    from weave.scorers import SummarizationScorer

    class SummarizationModel(weave.Model):
        @weave.op()
        async def predict(self, input: str) -> str:
            return "This is a summary of the input text."

    # Initialize clients and scorers
    llm_client = OpenAI()
    model = SummarizationModel()
    summarization_scorer = SummarizationScorer(
        client=llm_client,
        model_id="gpt-4o",
    )
    # Create dataset
    dataset = [
        {"input": "The quick brown fox jumps over the lazy dog."},
        {"input": "Artificial Intelligence is revolutionizing various industries."}
    ]

    # Run evaluation
    evaluation = weave.Evaluation(dataset=dataset, scorers=[summarization_scorer])
    results = asyncio.run(evaluation.evaluate(model))
    print(results)
    # {'SummarizationScorer': {'is_entity_dense': {'true_count': 0, 'true_fraction': 0.0}, 'summarization_eval_score': {'mean': 0.0}, 'entity_density': {'mean': 0.0}}, 'model_latency': {'mean': 6.210803985595703e-05}}
    ```

    ---

    ### `OpenAIModerationScorer`

    The `OpenAIModerationScorer` uses OpenAI's Moderation API to check if the AI system's output contains disallowed content, such as hate speech or explicit material.

    ```python
    from weave.scorers import OpenAIModerationScorer
    from openai import OpenAI

    oai_client = OpenAI(api_key=...) # initialize your LLM client here

    scorer = OpenAIModerationScorer(
        client=oai_client,
        model_id="text-embedding-3-small"
    )
    ```

    **How It Works:**

    - Sends the AI's output to the OpenAI Moderation endpoint and returns a dictionary indicating whether the content is flagged and details about the categories involved.

    **Notes:**

    - Requires the `openai` Python package.
    - The client must be an instance of OpenAI's `OpenAI` or `AsyncOpenAI` client.

    Here you have an example in the context of an evaluation:

    ```python
    import asyncio
    from openai import OpenAI
    import weave
    from weave.scorers import OpenAIModerationScorer

    class MyModel(weave.Model):
        @weave.op
        async def predict(self, input: str) -> str:
            return input

    # Initialize clients and scorers
    client = OpenAI()
    model = MyModel()
    moderation_scorer = OpenAIModerationScorer(client=client)

    # Create dataset
    dataset = [
        {"input": "I love puppies and kittens!"},
        {"input": "I hate everyone and want to hurt them."}
    ]

    # Run evaluation
    evaluation = weave.Evaluation(dataset=dataset, scorers=[moderation_scorer])
    results = asyncio.run(evaluation.evaluate(model))
    print(results)
    # {'OpenAIModerationScorer': {'flagged': {'true_count': 1, 'true_fraction': 0.5}, 'categories': {'violence': {'true_count': 1, 'true_fraction': 1.0}}}, 'model_latency': {'mean': 9.500980377197266e-05}}
    ```

    ---

    ### `EmbeddingSimilarityScorer`

    The `EmbeddingSimilarityScorer` computes the cosine similarity between the embeddings of the AI system's output and a target text from your dataset. It's useful for measuring how similar the AI's output is to a reference text.

    ```python
    from weave.scorers import EmbeddingSimilarityScorer

    llm_client = ...  # initialise your LlM client

    similarity_scorer = EmbeddingSimilarityScorer(
        client=llm_client
        target_column="reference_text",  # the dataset column to compare the output against
        threshold=0.4  # the cosine similarity threshold to use
    )
    ```

    **Parameters:**

    - `target`: This scorer expects a `target` column in your dataset, it will calculate the cosine similarity of the embeddings of the `target` column to the AI system output. If your dataset doesn't contain a column called `target` you can use the scorers `column_map` attribute to map `target` to the appropriate column name in your dataset. See the Column Mapping section for more.
    - `threshold` (float): The minimum cosine similarity score between the embedding of the AI system output and the embdedding of the `target`, above which the 2 samples are considered "similar", (defaults to `0.5`). `threshold` can be in a range from -1 to 1:
    - 1 indicates identical direction.
    - 0 indicates orthogonal vectors.
    - -1 indicates opposite direction.

    The correct cosine similarity threshold to set can fluctuate quite a lot depending on your use case, we advise exploring different thresholds.

    Here you have an example usage of the `EmbeddingSimilarityScorer` in the context of an evaluation:

    ```python
    import asyncio
    from openai import OpenAI
    import weave
    from weave.scorers import EmbeddingSimilarityScorer

    # Initialize clients and scorers
    client = OpenAI()
    similarity_scorer = EmbeddingSimilarityScorer(
        client=client,
        threshold=0.7,
        column_map={"target": "reference"}
    )

    # Create dataset
    dataset = [
        {
            "input": "He's name is John",
            "reference": "John likes various types of cheese.",
        },
        {
            "input": "He's name is Pepe.",
            "reference": "Pepe likes various types of cheese.",
        },
    ]

    # Define model
    @weave.op
    def model(input: str) -> str:
        return "John likes various types of cheese."

    # Run evaluation
    evaluation = weave.Evaluation(
        dataset=dataset,
        scorers=[similarity_scorer],
    )
    result = asyncio.run(evaluation.evaluate(model))
    print(result)
    # {'EmbeddingSimilarityScorer': {'is_similar': {'true_count': 1, 'true_fraction': 0.5}, 'similarity_score': {'mean': 0.8448514031462045}}, 'model_latency': {'mean': 0.45862746238708496}}
    ```

    ---

    ### `ValidJSONScorer`

    The ValidJSONScorer checks whether the AI system's output is valid JSON. This scorer is useful when you expect the output to be in JSON format and need to verify its validity.

    ```python
    from weave.scorers import ValidJSONScorer

    json_scorer = ValidJSONScorer()
    ```

    Here you have an example usage of the `ValidJSONScorer` in the context of an evaluation:

    ```python
    import asyncio
    import weave
    from weave.scorers import ValidJSONScorer

    class JSONModel(weave.Model):
        @weave.op()
        async def predict(self, input: str) -> str:
            # This is a placeholder.
            # In a real scenario, this would generate JSON.
            return '{"key": "value"}'

    model = JSONModel()
    json_scorer = ValidJSONScorer()

    dataset = [
        {"input": "Generate a JSON object with a key and value"},
        {"input": "Create an invalid JSON"}
    ]

    evaluation = weave.Evaluation(dataset=dataset, scorers=[json_scorer])
    results = asyncio.run(evaluation.evaluate(model))
    print(results)
    # {'ValidJSONScorer': {'json_valid': {'true_count': 2, 'true_fraction': 1.0}}, 'model_latency': {'mean': 8.58306884765625e-05}}
    ```

    ---

    ### `ValidXMLScorer`

    The `ValidXMLScorer` checks whether the AI system's output is valid XML. This is useful when expecting XML-formatted outputs.

    ```python
    from weave.scorers import ValidXMLScorer

    xml_scorer = ValidXMLScorer()
    ```

    Here you have an example usage of the `ValidXMLScorer` in the context of an evaluation:

    ```python
    import asyncio
    import weave
    from weave.scorers import ValidXMLScorer

    class XMLModel(weave.Model):
        @weave.op()
        async def predict(self, input: str) -> str:
            # This is a placeholder. In a real scenario, this would generate XML.
            return '<root><element>value</element></root>'

    model = XMLModel()
    xml_scorer = ValidXMLScorer()

    dataset = [
        {"input": "Generate a valid XML with a root element"},
        {"input": "Create an invalid XML"}
    ]

    evaluation = weave.Evaluation(dataset=dataset, scorers=[xml_scorer])
    results = asyncio.run(evaluation.evaluate(model))
    print(results)
    # {'ValidXMLScorer': {'xml_valid': {'true_count': 2, 'true_fraction': 1.0}}, 'model_latency': {'mean': 8.20159912109375e-05}}
    ```

    ---

    ### `PydanticScorer`

    The `PydanticScorer` validates the AI system's output against a Pydantic model to ensure it adheres to a specified schema or data structure.

    ```python
    from weave.scorers import PydanticScorer
    from pydantic import BaseModel

    class FinancialReport(BaseModel):
        revenue: int
        year: str

    pydantic_scorer = PydanticScorer(model=FinancialReport)
    ```

    ---

    ### RAGAS - `ContextEntityRecallScorer`

    The `ContextEntityRecallScorer` estimates context recall by extracting entities from both the AI system's output and the provided context, then computing the recall score. Based on the [RAGAS](https://github.com/explodinggradients/ragas) evaluation library

    ```python
    from weave.scorers import ContextEntityRecallScorer

    llm_client = ...  # initialise your LlM client

    entity_recall_scorer = ContextEntityRecallScorer(
        client=llm_client
        model_id="your-model-id"
    )
    ```

    **How It Works:**

    - Uses an LLM to extract unique entities from the output and context and calculates recall.
    - **Recall** indicates the proportion of important entities from the context that are captured in the output, helping to assess the model's effectiveness in retrieving relevant information.
    - Returns a dictionary with the recall score.

    **Notes:**

    - Expects a `context` column in your dataset, use `column_map` to map `context` to another dataset column if needed.

    ---

    ### RAGAS - `ContextRelevancyScorer`

    The `ContextRelevancyScorer` evaluates the relevancy of the provided context to the AI system's output. It helps determine if the context used is appropriate for generating the output. Based on the [RAGAS](https://github.com/explodinggradients/ragas) evaluation library.

    ```python
    from weave.scorers import ContextRelevancyScorer

    llm_client = ...  # initialise your LlM client

    relevancy_scorer = ContextRelevancyScorer(
        llm_client = ...  # initialise your LlM client
        model_id="your-model-id"
        )
    ```

    **How It Works:**

    - Uses an LLM to rate the relevancy of the context to the output on a scale from 0 to 1.
    - Returns a dictionary with the `relevancy_score`.

    **Notes:**

    - Expects a `context` column in your dataset, use `column_map` to map `context` to another dataset column if needed.
    - Customize the `relevancy_prompt` to define how relevancy is assessed.

    Here you have an example usage of `ContextEntityRecallScorer` and `ContextRelevancyScorer` in the context of an evaluation:

    ```python
    import asyncio
    from textwrap import dedent
    from openai import OpenAI
    import weave
    from weave.scorers import ContextEntityRecallScorer, ContextRelevancyScorer

    class RAGModel(weave.Model):
        @weave.op()
        async def predict(self, question: str) -> str:
            "Retrieve relevant context"
            return "Paris is the capital of France."


    model = RAGModel()

    # Define prompts
    relevancy_prompt: str = dedent("""
        Given the following question and context, rate the relevancy of the context to the question on a scale from 0 to 1.

        Question: {question}
        Context: {context}
        Relevancy Score (0-1):
        """)

    # Initialize clients and scorers
    llm_client = OpenAI()
    entity_recall_scorer = ContextEntityRecallScorer(
        client=client,
        model_id="gpt-4o",
    )

    relevancy_scorer = ContextRelevancyScorer(
        client=llm_client,
        model_id="gpt-4o",
        relevancy_prompt=relevancy_prompt
    )

    # Create dataset
    dataset = [
        {
            "question": "What is the capital of France?",
            "context": "Paris is the capital city of France."
        },
        {
            "question": "Who wrote Romeo and Juliet?",
            "context": "William Shakespeare wrote many famous plays."
        }
    ]

    # Run evaluation
    evaluation = weave.Evaluation(
        dataset=dataset,
        scorers=[entity_recall_scorer, relevancy_scorer]
    )
    results = asyncio.run(evaluation.evaluate(model))
    print(results)
    # {'ContextEntityRecallScorer': {'recall': {'mean': 0.3333333333333333}}, 'ContextRelevancyScorer': {'relevancy_score': {'mean': 0.5}}, 'model_latency': {'mean': 9.393692016601562e-05}}
    ```

  </TabItem>
  <TabItem value="typescript" label="TypeScript">
    ```plaintext
    This feature is not available in TypeScript yet.  Stay tuned!
    ```
  </TabItem>
</Tabs>
