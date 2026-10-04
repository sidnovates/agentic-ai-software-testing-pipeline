## INTERNATIONAL INSTITUTE OF INFORMATION TECHNOLOGY BANGALORE

Mid-term Project - Term I (2026-27)

CSE731: Software Testing

The purpose of this mid-term project is to learn how to set up an agentic AI pipeline that will generate unit test cases that serve a specific testing goal at the unit level of testing. Unit testing involves validating individual functional units of a software application to ensure that they pass the required test cases, which in turn, implies that they function as expected. The project is expected to be done in teams of two members, the teams can be decided by the students themselves.

The students are expected to use AI tools to build a simple agentic AI pipeline that minimally consists of three agents: A code generator agent that generates unit level code, a test case generator agent that generates unit test cases for the code and a test case executor agent that executes the generates test cases and provides a verdict regarding the exe- cution. The test case generator agent is expected to generate test cases satisfying one of the following requirements: (1) Achieve a user-specified coverage criterion (for e.g., cover all statements, cover all loops, cover all decision statements etc.), (2) Achieve a user-specified property about the function representing the unit of code (for e.g., if the code is about finding an element in a list, the property should state the expected output when the element is found, not found etc.), (3) Apply a simple statistical estimation method against multiple runs (for e.g., statistically estimate the probability that at least one generated suite is correct given a total number of samples).

Possible data-sets that you could consider using for unit testing include MBPP (Most Basic Python Problems) or HumanEval as inputs to your agentic AI unit testing pipeline. Free tokens can be obtained from a few sources like KiloAI, OpenRouter Free Models or other reliable sources that you find on the internet.

The project begins on 29 September 2026 and will close on 1 October 2026. A dedicated submission portal will be available in the course page LMS to upload the project report, one report per team. Demos will be taken during the lecture slots on 1, 6 and 8 October 2026. Everyone is expected to be present for the demo sessions.

You have to submit the following details as a part of your project report:

- 1. The Agentic AI pipeline developed by your team, starting with the dataset used and including the considered functionality of the test-case generator pipeline.

- 2. The user prompts and the system-generated prompts and settings (including temperature value and other param- eters) for the pipeline.

- 3. The format of the code and the test cases generated and the verdict, along with the actual code and the test cases.

- 4. If pursuing statistical testing, metrics that you considered for statistical evaluation. If pursuing coverage or property-based testing, the execution results of the test case generator and the test case executor agents.

- 5. Each member’s contribution to the project.

Please do not use any RAG pipelines or any chain of thought concepts or frameworks like LangGraph in your agentic AI application. The purpose of the agentic AI pipeline that you will develop is for you to learn from first principles how to set up a pipeline and execute a set of unit test cases that are generated to meet a test requirement.

All the best!
