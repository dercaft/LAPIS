# LAPIS (Longform Automated Progressive Interfacing Scriber)

LAPIS is an intelligent writing assistance system that enables progressive and interactive longform content generation through automated agent workflows.

## 🌟 Features

- **Automated Outline Generation**: Initial content structure creation with user refinement
- **Visual Structure Mapping**: 
  - Fishbone diagrams for structural relationships
  - Directed graphs for content flow visualization
- **Progressive Content Generation**: Section-by-section automated writing with user feedback
- **Interactive Refinement**:
  - Node relationship modification
  - Content adjustment capabilities
  - Paragraph-level editing

## 🛠️ Core Components

- **Agentic Workflow Engine**: Manages the automated content generation pipeline
- **Interactive GUI**: User interface for content visualization and modification
- **Content Processing System**: Handles section-wise content generation and updates

## Quickstart

Follow these steps to get started with LAPIS:

### Setup

1. (Optional) Create and activate a Python virtual environment:
    
```shell
python3 -m venv venv
source venv/bin/activate
```

2. Install the required dependencies:
        
```shell 
pip install chainlit pyautogen
```

3. Copy the `.env.sample` file to a new `.env` file and replace the `api_key` value with your own OpenAI API key.
4. Run the Chainlit app:

### Notes

- Do not run with `chainlit run app.py -w` as it may cause unexpected behavior.
- You can monkey-patch methods of the `Agent` class if needed, instead of creating a subclass.

## Code Overview

The `app.py` file contains the main logic for the Chainlit chat application. It defines custom `Agent` classes that handle sending messages and processing user input.

- `ChainlitAssistantAgent`: A subclass of `AssistantAgent` that sends messages to other agents.
- `ChainlitUserProxyAgent`: A subclass of `UserProxyAgent` that handles user input and can send messages to other agents.

The `async_app.py` file is a placeholder for future asynchronous support, pending the resolution of an issue in the AutoGen library.

To change the task, modify the `TASK` variable in `app.py` with the desired prompt.

## Running the Application

To start the application, use the following command: 
    
```shell
chainlit run app.py
```

This will initiate a chat session where the user can interact with the assistant agent to perform tasks such as generating content outlines and progressive content generation.

## 🔄 Workflow

1. **Outline Phase**
   - System generates initial outline
   - User reviews and modifies
   - Visual structure maps are created

2. **Content Generation Phase**
   - Section-by-section automated writing
   - User feedback integration
   - Progressive refinement

3. **Refinement Phase**
   - Node relationship adjustments
   - Content optimization
   - Final review and export

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [AutoGen](https://microsoft.github.io/autogen/)
- [Chainlit](https://github.com/Chainlit/chainlit)

For more detailed information on the functions and classes used, refer to the source code in the `app.py` and `async_app.py` files.
