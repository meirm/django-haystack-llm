# django-haystack-llm

## Django-Haystack LLM Enhanced Search Backend

## Overview

This Django-Haystack implementation introduces an ORM-based search backend, `EnglishSearchBackend`, enhanced with Large Language Model (LLM) technology for generating semantic query alternatives. Designed primarily for testing and demonstration purposes, it offers a simple yet powerful example of integrating LLMs with Django-Haystack to perform semantic search operations.

## Features

- **ORM-Based Backend**: Utilizes Django's Object-Relational Mapping (ORM) for search operations, allowing for easy integration with Django models.
- **LLM Semantic Query Alternation**: Employs an LLM (specifically OpenAI's GPT-3.5 model) to translate non-English queries into English or generate semantically similar English queries if the initial search yields no results.
- **Environmental Variable Management**: Leverages `.env` files for secure and flexible configuration, specifically for managing the OpenAI API key.
- **Flexible Query Processing**: Supports processing both direct model field searches and semantically similar queries through LLM intervention, enhancing the breadth of search capabilities.

## Setup

### Prerequisites

- Django and Django-Haystack installed in your project.
- Access to OpenAI's API and an API key.
- Python `dotenv` package for loading environmental variables.

### Installation

1. **Install Dependencies**: Ensure you have Django, Django-Haystack, and the `python-dotenv` package installed in your environment.
   ```bash
   pip install django haystack python-dotenv
   ```

2. **Configure `.env` File**: Create a `.env` file in your project root and add your OpenAI API key.
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Update Django Settings**: Add or update the `HAYSTACK_CONNECTIONS` setting in your project's `settings.py` to use `EnglishEngine` as the search engine.
   ```python
   HAYSTACK_CONNECTIONS = {
       'default': {
           'ENGINE': 'path.to.EnglishEngine',
       },
   }
   ```

4. **Integrate Backend Code**: Include the `EnglishSearchBackend`, `SimpleSearchQuery`, and `EnglishEngine` classes in your project. These can be placed in a module (e.g., `english_search_backend.py`) that's accessible from your Django settings.

### Usage

Use Haystack's search features as you normally would. The `EnglishSearchBackend` will automatically translate non-English queries into English or generate semantically similar queries as needed, leveraging the LLM to enhance search results.

## How It Works

- The backend first attempts a standard ORM-based search with the given query string.
- If the initial search yields no results, it invokes an LLM chain to translate the query into English or to generate a semantically similar English query.
- The modified query is then used for a second search attempt. This step is skipped if the `skip_llm_query` flag is set to `True` in `kwargs` to prevent recursive LLM processing.

## Limitations

- Designed for demonstration and testing purposes, not optimized for production use.
- Dependent on external API (OpenAI) availability and subject to its rate limits and costs.
- Performance may vary based on the complexity of queries and the efficiency of the ORM-based search implementation.

## Contributing

Contributions to enhance the functionality, improve performance, or extend compatibility are welcome. Please follow standard open-source contribution guidelines when proposing changes or additions.
