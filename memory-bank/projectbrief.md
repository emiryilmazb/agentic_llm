# Project Brief

## Project Overview
This project is a chatbot platform system that allows users to interact with AI characters. The system consists of a backend API built with Python (likely using FastAPI based on the structure) and a React frontend.

## Core Requirement
The current task is to separate conversation history from characters so that a user can have multiple distinct conversations with the same character. This means modifying the data model and API to support multiple chat sessions per character.

## Goals
1. Modify the database structure to separate character definitions from conversation history
2. Update the API to support creating and retrieving multiple conversations with the same character
3. Update the frontend to support selecting different conversations with the same character
4. Ensure backward compatibility with existing data if possible

## Success Criteria
- Users can start new conversations with the same character without losing previous conversation history
- Users can switch between different conversations they've had with the same character
- The character's core attributes and personality remain consistent across conversations
