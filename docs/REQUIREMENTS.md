Software Framework for comparative analysis of AI-based coding assistants Description: the goal of this project is to design and develop software framework to compare at least four popular AI-based coding assistants (software tools that can generate the source code), including GitHub Copilot. For comparative analysis, your software framework should consider the following factors: 

1. Supported programming languages, 
2. Bugs and errors in the generated code, 
3. Security vulnerabilities in the generated code and proposed mitigation mechanisms, 
4. Documentation and code readability, 
5. Efficiency and performance of the generated code. 

AI-based coding assistants must be tested and evaluated based on the programming tasks to generate the source code for the following:  

- Read data from text file,  
- Read data values from JSON file using multiple threads,  
- Write data into text file,  
- Write data values into JSON file using multiple threads, 
- Produce zip archive by calling an external application for the input text file supplied as an argument, 
- Connect to MySQL relational database and retrieve a sample database record from a table, 
- Connect to MongoDB non-relational database and retrieve a sample database record from a data collection,  
- JavaScript or PHP (or similar) code for password-based authentication that can be embedded into a web page.  

Your software should: (1) provide GUI to choose the software coding task; (2) create a report with the generated source code and relevant quality metrics, including the following: 

- (2.1) Does the generated source code compile without errors?  
- (2.2) Does the generated source code do what it is supposed to do?  
- (2.3) Are there any warnings when the generated source code is compiled or interpreted?  
- (2.4) Are there any security vulnerabilities in the generated code? 

 

Note: static analysis tool such as "Coverity" can be used to scan the generated source code for security vulnerabilities and help with the code evaluation. Using your results, choose the best AI-based Coding Assistant tool for each programming task listed above.

## Research-Focused Extended Requirements

### Core Research Objectives

VibeBench is designed as a research framework to evaluate and compare AI-based coding assistants across standardized programming tasks. The project aims to:

1. **Produce publishable research findings** on comparative capabilities of AI coding assistants
2. **Establish reproducible benchmarking methodology** for code generation quality evaluation
3. **Create open-source reference implementation** for academic community
4. **Generate datasets** for further research on LLM code generation

### Key Features for Research Impact

**1. Comprehensive Quality Metrics**
- Compilation/execution success rates
- Functional correctness verification
- Security vulnerability detection (OWASP Top 10 mapping)
- Code readability and maintainability analysis
- Performance profiling (execution time, memory usage)

**2. Historical Trend Analysis**
- Track how model capabilities improve over time
- Compare versions: GPT-3.5 → GPT-4, Copilot v1 → v2
- Document findings for conference/journal publications
- Store model versions and dates for reproducibility

**3. Security Analysis (Research-Grade)**
- Categorize vulnerabilities by type (CWE, OWASP)
- Quantify security patterns in AI-generated code
- Publish findings: "Common security mistakes in AI code generation"
- Create vulnerability dataset for ML community

**4. Cost-Effectiveness Study**
- Track API costs per model
- Analyze quality vs. cost tradeoffs
- Publish: "Cost-effectiveness of AI coding assistants" (research paper)
- Dataset: Open cost benchmarks for reproducibility

**5. Simple Results Repository**
- GitHub-based storage of benchmark results
- CSV/JSON exports for meta-analysis
- Public dataset for other researchers to analyze
- Transparency: All prompts and generated code available

### Non-Requirements (Out of Scope for Research)

**What we're NOT building:**
- ❌ Enterprise CI/CD pipelines (focus on core research, not deployment)
- ❌ Multi-tenant SaaS platform (research publication > product)
- ❌ Compliance reporting (regulatory focus, not research)
- ❌ Advanced ML models for predictions (stick to descriptive analysis)
- ❌ Custom task engines (focus on standard 8 tasks)
- ❌ Fine-tuning LLMs (research project, not ML engineering)
- ❌ Real-time dashboards (static reports sufficient)
- ❌ Multiple cloud regions (run on single lab server)

## Research Positioning

**Research Goal:**
VibeBench produces the first comprehensive, independent, reproducible evaluation of AI-based coding assistants across standardized programming tasks. The framework is designed for academic research and will be published with open-source code and publicly available datasets.

**Target Audience:**
- Computer Science researchers studying LLM code generation
- ML/AI conferences and journals (ICML, NeurIPS, ACL, FSE, ICSE)
- Student researchers evaluating AI tools
- Open-source community studying AI capabilities and limitations

**Research Contributions:**
1. Standardized benchmarking methodology for code generation
2. Comparative evaluation dataset (public, reproducible)
3. Analysis of security vulnerabilities in AI-generated code
4. Documentation of model evolution over time
5. Cost-effectiveness analysis of different AI models
6. Methodology and code available for others to extend

**Publication Venues:**
- IEEE Transactions on Software Engineering (TSE)
- ACM Transactions on Software Engineering and Methodology (TOSEM)
- Empirical Software Engineering conference (EMSE)
- Mining Software Repositories (MSR) conference
- International Conference on Software Engineering (ICSE)

 